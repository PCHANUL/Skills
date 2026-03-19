import argparse
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

DEFAULT_PROGRESS_FILE = "TASK_PROGRESS.md"
TASK_MARKER = "## Task Checklist"


def run_command(
    cmd_list: List[str],
    *,
    check: bool = True,
    capture_output: bool = True,
    text: bool = True,
) -> Optional[str]:
    try:
        result = subprocess.run(
            cmd_list,
            capture_output=capture_output,
            text=text,
            check=check,
        )
        if capture_output:
            return result.stdout.strip()
        return ""
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.strip() if error.stderr else ""
        print(f"Error running command: {' '.join(cmd_list)}")
        if stderr:
            print(stderr)
        if check:
            sys.exit(1)
        return None


def run_shell_command(command: str) -> Tuple[bool, str]:
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    combined = "\n".join(
        part.strip()
        for part in [result.stdout or "", result.stderr or ""]
        if part and part.strip()
    ).strip()
    return result.returncode == 0, combined


def read_progress_file(path: str) -> Dict[str, object]:
    data: Dict[str, object] = {
        "sections": {},
        "tasks": [],
    }
    if not os.path.exists(path):
        return data

    with open(path, "r", encoding="utf-8") as file:
        lines = [line.rstrip("\n") for line in file]

    current_section: Optional[str] = None
    in_tasks = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped == TASK_MARKER:
            current_section = None
            in_tasks = True
            continue

        if stripped.startswith("## "):
            current_section = stripped[3:]
            if current_section != "Task Checklist":
                data["sections"].setdefault(current_section, [])
            in_tasks = current_section == "Task Checklist"
            continue

        if in_tasks and stripped.startswith("- ["):
            match = re.match(r"- \[( |x)\] (\d+)\.\s+(.*)", stripped)
            if match:
                data["tasks"].append(
                    {
                        "done": match.group(1) == "x",
                        "index": int(match.group(2)),
                        "text": match.group(3).strip(),
                    }
                )
            continue

        if current_section and stripped.startswith("- "):
            data["sections"][current_section].append(stripped[2:].strip())

    return data


def section_items(progress: Dict[str, object], name: str) -> List[str]:
    sections = progress.get("sections", {})
    if not isinstance(sections, dict):
        return []
    items = sections.get(name, [])
    return items if isinstance(items, list) else []


def completed_tasks(progress: Dict[str, object]) -> List[str]:
    tasks = progress.get("tasks", [])
    if not isinstance(tasks, list):
        return []
    return [task["text"] for task in tasks if task.get("done")]


def incomplete_tasks(progress: Dict[str, object]) -> List[str]:
    tasks = progress.get("tasks", [])
    if not isinstance(tasks, list):
        return []
    return [task["text"] for task in tasks if not task.get("done")]


def progress_title(progress: Dict[str, object]) -> Optional[str]:
    for item in section_items(progress, "Issue"):
        if item.startswith("Title:"):
            return item.replace("Title:", "", 1).strip()
    return None


def progress_source(progress: Dict[str, object]) -> Optional[str]:
    for item in section_items(progress, "Issue"):
        if item.startswith("Source:"):
            return item.replace("Source:", "", 1).strip()
    return None


def check_existing_pr() -> Optional[Dict[str, object]]:
    current_branch = run_command(["git", "branch", "--show-current"])
    print(f"Checking for existing PR on {current_branch}...")

    output = run_command(
        ["gh", "pr", "list", "--head", current_branch, "--json", "url,number,state"],
        check=False,
    )
    if not output:
        return None

    prs = json.loads(output)
    if not prs:
        return None

    pr = prs[0]
    print(f"Existing PR found: #{pr['number']} ({pr['state']})")
    print(f"URL: {pr['url']}")
    return pr


def detect_base_branch(issue_num: int) -> str:
    milestone = run_command(
        ["gh", "issue", "view", str(issue_num), "--json", "milestone", "--jq", ".milestone.title"],
        check=False,
    )
    if milestone:
        match = re.search(r"Phase\s+(\d+)", milestone, re.IGNORECASE)
        if match:
            base_branch = f"milestone/phase-{match.group(1)}"
            print(f"Detected integration branch from milestone '{milestone}': {base_branch}")
            return base_branch
        print(f"Warning: Could not parse phase from milestone '{milestone}'. Defaulting to main.")
    return "main"


def resolve_target_ref(base_branch: str) -> str:
    remote_check = run_command(["git", "ls-remote", "--heads", "origin", base_branch], check=False)
    if remote_check:
        return f"origin/{base_branch}"

    print(f"Warning: remote branch {base_branch} not found. Diffing against origin/main.")
    return "origin/main"


def commit_summary(target_ref: str) -> str:
    commits = run_command(
        ["git", "log", "--no-merges", "--pretty=format:- %s", f"{target_ref}..HEAD"],
        check=False,
    )
    if commits:
        return commits
    return "- No commit summary available relative to base branch."


def debugger_script_path() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    skills_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(skills_root, "project-task-debugger", "scripts", "debug.py")


def run_debugger(command: str) -> bool:
    script = debugger_script_path()
    if not os.path.exists(script):
        print(f"Debugger script not found at {script}.")
        return False

    result = subprocess.run(["python3", script, "--command", command], check=False)
    return result.returncode == 0


def run_verifications(
    commands: List[str],
    *,
    use_debugger: bool = False,
) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    for command in commands:
        print(f"Running verification: {command}")
        ok, output = run_shell_command(command)
        status = "passed" if ok else "failed"

        if not ok and use_debugger:
            print(f"Verification failed. Trying debugger for: {command}")
            debug_ok = run_debugger(command)
            if debug_ok:
                ok, output = run_shell_command(command)
                status = "passed" if ok else "failed"

        results.append(
            {
                "command": command,
                "status": status,
                "output": output,
            }
        )
        if not ok:
            break
    return results


def format_bullets(items: List[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def format_verification_results(results: List[Dict[str, str]], planned: List[str]) -> str:
    if results:
        return "\n".join(
            f"- `{item['command']}`: {item['status']}"
            for item in results
        )
    if planned:
        return "\n".join(f"- Planned: `{command}`" for command in planned)
    return "- No verification steps were provided."


def build_pr_body(
    issue_num: int,
    progress: Dict[str, object],
    verification_results: List[Dict[str, str]],
    planned_verification: List[str],
    commit_lines: str,
) -> str:
    source = progress_source(progress)
    target_outcome = section_items(progress, "Target outcome")
    done_items = section_items(progress, "Definition of done")
    completed = completed_tasks(progress)
    remaining = incomplete_tasks(progress)

    parts: List[str] = [f"Closes #{issue_num}"]

    if source:
        parts.extend(["", f"Source of truth: `{source}`"])

    parts.extend(
        [
            "",
            "## Target Outcome",
            format_bullets(target_outcome, "No target outcome recorded."),
            "",
            "## Completed Work",
            format_bullets(completed, "No completed task checklist found."),
            "",
            "## Definition Of Done",
            format_bullets(done_items, "No definition of done recorded."),
            "",
            "## Verification",
            format_verification_results(verification_results, planned_verification),
        ]
    )

    if remaining:
        parts.extend(["", "## Remaining Gaps", format_bullets(remaining, "None.")])

    parts.extend(["", "## Commit Summary", commit_lines])
    return "\n".join(parts)


def ensure_clean_completion(progress: Dict[str, object], allow_incomplete: bool, draft: bool) -> None:
    remaining = incomplete_tasks(progress)
    if not remaining:
        return

    print("Incomplete tasks detected in TASK_PROGRESS.md:")
    for task in remaining:
        print(f"- {task}")

    if allow_incomplete or draft:
        return

    print("Refusing to finish a non-draft PR while tracked tasks remain incomplete.")
    sys.exit(1)


def stage_and_commit(issue_num: int, progress: Dict[str, object]) -> None:
    print("Committing changes...")
    run_command(["git", "add", "."])

    status = run_command(["git", "status", "--porcelain"])
    if not status:
        print("No changes to commit.")
        return

    title = progress_title(progress)
    if title:
        commit_msg = f"feat: {title} (#{issue_num})"
    else:
        commit_msg = f"feat: Implement Issue #{issue_num}"
    run_command(["git", "commit", "-m", commit_msg], check=False)


def create_or_update_pr(
    issue_num: int,
    title: str,
    body: str,
    *,
    base_branch: str,
    draft: bool,
) -> str:
    existing_pr = check_existing_pr()
    if existing_pr:
        print("Updating existing PR...")
        edit_cmd = [
            "gh",
            "pr",
            "edit",
            str(existing_pr["number"]),
            "--title",
            title,
            "--body",
            body,
        ]
        run_command(edit_cmd)
        if not draft:
            run_command(["gh", "pr", "ready", str(existing_pr["number"])], check=False)
        return str(existing_pr["url"])

    print("Creating new PR...")
    pr_cmd = [
        "gh",
        "pr",
        "create",
        "--title",
        title,
        "--body",
        body,
        "--base",
        base_branch,
    ]
    if draft:
        pr_cmd.append("--draft")
    pr_url = run_command(pr_cmd)
    print(f"PR Created: {pr_url}")
    return pr_url or ""


def issue_title(issue_num: int, progress: Dict[str, object]) -> str:
    title = run_command(
        ["gh", "issue", "view", str(issue_num), "--json", "title", "--jq", ".title"],
        check=False,
    )
    if title:
        return title

    stored = progress_title(progress)
    if stored:
        return stored

    return f"Issue #{issue_num}"


def comment_on_issue(issue_num: int, pr_url: str, verification_results: List[Dict[str, str]], planned: List[str]) -> None:
    verification = format_verification_results(verification_results, planned)
    body = "\n".join(
        [
            f"Linked to PR: {pr_url}",
            "",
            "Verification summary:",
            verification,
        ]
    )
    run_command(["gh", "issue", "comment", str(issue_num), "--body", body], check=False)
    run_command(["gh", "issue", "edit", str(issue_num), "--remove-label", "in-progress"], check=False)


def finish_task(args: argparse.Namespace) -> None:
    progress = read_progress_file(args.progress_file)
    ensure_clean_completion(progress, args.allow_incomplete, args.draft)

    verification_commands = list(args.verification_cmd or [])
    if args.use_progress_verification:
        verification_commands.extend(section_items(progress, "Verification"))

    if args.test_cmd:
        verification_commands = list(args.test_cmd) + verification_commands

    verification_results = run_verifications(
        verification_commands,
        use_debugger=args.use_debugger,
    )

    if verification_results and verification_results[-1]["status"] == "failed" and not args.draft:
        print("Verification failed. Aborting finish.")
        sys.exit(1)

    if args.dry_run:
        title = progress_title(progress) or f"Issue #{args.issue}"
        body = build_pr_body(
            args.issue,
            progress,
            verification_results,
            verification_commands,
            "- Dry run: commit summary not generated.",
        )
        print("\n--- DRY RUN PR TITLE ---")
        print(title)
        print("\n--- DRY RUN PR BODY ---")
        print(body)
        return

    stage_and_commit(args.issue, progress)

    current_branch = run_command(["git", "branch", "--show-current"])
    print(f"Pushing {current_branch}...")
    run_command(["git", "push", "-u", "origin", current_branch])

    base_branch = detect_base_branch(args.issue)
    target_ref = resolve_target_ref(base_branch)
    commits = commit_summary(target_ref)
    title = issue_title(args.issue, progress)
    body = build_pr_body(args.issue, progress, verification_results, verification_commands, commits)

    pr_url = create_or_update_pr(
        args.issue,
        title,
        body,
        base_branch=base_branch,
        draft=args.draft,
    )
    comment_on_issue(args.issue, pr_url, verification_results, verification_commands)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Finish a task by verifying, committing, and creating a PR.")
    parser.add_argument("--issue", type=int, required=True, help="Issue number being finished")
    parser.add_argument(
        "--progress-file",
        default=DEFAULT_PROGRESS_FILE,
        help=f"Path to progress file (default: {DEFAULT_PROGRESS_FILE})",
    )
    parser.add_argument(
        "--test-cmd",
        action="append",
        default=[],
        help="Test command to run before finishing. Can be passed multiple times.",
    )
    parser.add_argument(
        "--verification-cmd",
        action="append",
        default=[],
        help="Additional verification command to run before finishing. Can be passed multiple times.",
    )
    parser.add_argument(
        "--use-progress-verification",
        action="store_true",
        help="Run commands listed in the progress file Verification section.",
    )
    parser.add_argument(
        "--use-debugger",
        action="store_true",
        help="If a verification command fails, try project-task-debugger before aborting.",
    )
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow finishing even if unchecked tasks remain in the progress file.",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Create or keep the PR as draft. Useful when verification or scope is incomplete.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated PR title/body after verification and push logic setup without touching GitHub.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    finish_task(args)


if __name__ == "__main__":
    main()
