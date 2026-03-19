import argparse
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional

STATE_FILE = "DRIVER_STATE.json"
PROGRESS_FILE = "TASK_PROGRESS.md"
CONTEXT_HEADINGS = [
    "Why this week exists",
    "Read first",
    "Current code reality",
    "Target outcome",
    "Files likely touched",
    "Out of scope",
    "Definition of done",
    "Verification",
]


def run_command(cmd_list: List[str], fatal: bool = True) -> Optional[str]:
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.strip() if error.stderr else ""
        print(f"\n[ERROR] Command failed: {' '.join(cmd_list)}")
        if stderr:
            print(stderr)
        if fatal:
            sys.exit(1)
        return None


def run_python_script(path: str, args: List[str]) -> int:
    result = subprocess.run(["python3", path, *args], check=False)
    return result.returncode


def run_json_script(path: str, args: List[str]) -> Dict[str, object]:
    result = subprocess.run(["python3", path, *args], capture_output=True, text=True, check=False)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())

    payload = result.stdout.strip() if result.stdout else ""
    if not payload:
        return {"status": "fail", "error": "No review output produced."}

    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {
            "status": "fail",
            "error": "Review output was not valid JSON.",
            "raw_output": payload,
        }


def get_open_issues(milestone_title: str) -> List[Dict[str, object]]:
    output = run_command(
        [
            "gh",
            "issue",
            "list",
            "--milestone",
            milestone_title,
            "--state",
            "open",
            "--json",
            "number,title,state,milestone",
            "--limit",
            "100",
        ],
        fatal=False,
    )
    if not output:
        return []

    issues = json.loads(output)
    issues.sort(key=lambda item: item["number"])
    return issues


def get_issue_details(issue_num: int) -> Dict[str, object]:
    output = run_command(
        ["gh", "issue", "view", str(issue_num), "--json", "number,title,body,milestone"],
        fatal=False,
    )
    if not output:
        return {"number": issue_num, "title": f"Issue #{issue_num}", "body": ""}
    return json.loads(output)


def normalize_heading(line: str) -> Optional[str]:
    stripped = line.strip()
    if stripped.startswith("**") and stripped.endswith("**"):
        return stripped[2:-2].strip()
    if stripped.startswith("## "):
        return stripped[3:].strip()
    return None


def extract_context_sections(body: str) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {heading: [] for heading in CONTEXT_HEADINGS}
    current: Optional[str] = None

    for raw_line in body.splitlines():
        heading = normalize_heading(raw_line)
        if heading in sections:
            current = heading
            continue
        if heading and heading not in sections:
            current = None
            continue

        if current:
            line = raw_line.rstrip()
            if line.strip():
                sections[current].append(line)

    return sections


def print_issue_context(issue: Dict[str, object]) -> None:
    print("\n[Driver] Issue context")
    print(f"Title: {issue.get('title', '')}")
    sections = extract_context_sections(str(issue.get("body", "")))
    for heading in ["Read first", "Current code reality", "Target outcome", "Definition of done", "Verification"]:
        values = sections.get(heading, [])
        if not values:
            continue
        print(f"\n{heading}:")
        for value in values[:8]:
            print(value)

    if not os.path.exists(PROGRESS_FILE):
        print(f"\n[Driver] Note: `{PROGRESS_FILE}` does not exist yet. The implementer should initialize it before coding.")


def save_state(milestone: str, issue_num: int) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump({"milestone": milestone, "current_issue": issue_num}, file)
    print(f"[Driver] State saved: {milestone} / Issue #{issue_num}")


def load_state() -> Optional[Dict[str, object]]:
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def clear_state() -> None:
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    print("[Driver] State cleared.")


def detect_integration_branch(milestone_title: str) -> str:
    match = re.search(r"Phase\s+(\d+)", milestone_title, re.IGNORECASE)
    if match:
        return f"milestone/phase-{match.group(1)}"
    return "main"


def skills_root() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(current_dir))


def script_path(skill_name: str, script_name: str) -> str:
    return os.path.join(skills_root(), skill_name, "scripts", script_name)


def ensure_integration_branch(branch: str) -> None:
    print(f"[Driver] Switching to {branch}...")
    run_command(["git", "fetch", "origin"], fatal=False)
    run_command(["git", "checkout", branch])
    run_command(["git", "pull", "origin", branch], fatal=False)


def current_pr() -> Optional[Dict[str, object]]:
    branch = run_command(["git", "branch", "--show-current"], fatal=False)
    if not branch:
        return None
    output = run_command(
        ["gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number,url,title", "--limit", "1"],
        fatal=False,
    )
    if not output:
        return None
    prs = json.loads(output)
    return prs[0] if prs else None


def merge_pr(pr_number: int) -> None:
    run_command(["gh", "pr", "merge", str(pr_number), "--merge", "--delete-branch"])


def close_issue(issue_num: int) -> None:
    run_command(["gh", "issue", "close", str(issue_num)], fatal=False)


def update_integration_pr(integration_branch: str, issue_num: int, issue_title: str) -> None:
    output = run_command(
        [
            "gh",
            "pr",
            "list",
            "--head",
            integration_branch,
            "--state",
            "open",
            "--json",
            "number,body",
            "--limit",
            "1",
        ],
        fatal=False,
    )
    if not output:
        return

    prs = json.loads(output)
    if not prs:
        return

    current_body = prs[0].get("body") or ""
    new_line = f"- [x] Completed Issue #{issue_num}: {issue_title}"
    if new_line in current_body:
        return
    new_body = f"{current_body}\n{new_line}".strip()
    run_command(["gh", "pr", "edit", str(prs[0]["number"]), "--body", new_body], fatal=False)


def first_failed_verification(review_result: Dict[str, object]) -> Optional[str]:
    verification = review_result.get("verification_results", [])
    if not isinstance(verification, list):
        return None
    for item in verification:
        if isinstance(item, dict) and item.get("status") == "failed":
            return str(item.get("command"))
    return None


def print_review_failures(review_result: Dict[str, object]) -> None:
    print("[Driver] Review failed.")
    incomplete = review_result.get("incomplete_tasks", [])
    if isinstance(incomplete, list) and incomplete:
        print("Incomplete tasks:")
        for task in incomplete:
            print(f"- {task}")

    verification = review_result.get("verification_results", [])
    if isinstance(verification, list) and verification:
        print("Verification results:")
        for item in verification:
            if isinstance(item, dict):
                print(f"- {item.get('command')}: {item.get('status')}")

    if "error" in review_result:
        print(f"Review error: {review_result['error']}")


def create_release_pr(milestone_title: str, integration_branch: str) -> None:
    print(f"\n[Driver] Creating release PR for {milestone_title}...")
    output = run_command(
        ["gh", "issue", "list", "--milestone", milestone_title, "--state", "closed", "--json", "number,title"],
        fatal=False,
    )
    closed_issues = json.loads(output) if output else []

    body_lines = [
        f"# Release: {milestone_title}",
        "",
        "## Released Features",
        "",
    ]
    if closed_issues:
        for issue in closed_issues:
            body_lines.append(f"- Closes #{issue['number']}: {issue['title']}")
    else:
        body_lines.append("- No closed issues found for this milestone.")

    body_lines.extend(["", "## Integration Details", f"Merges `{integration_branch}` into `main`."])
    body = "\n".join(body_lines)

    run_command(
        [
            "gh",
            "pr",
            "create",
            "--title",
            f"Release: {milestone_title}",
            "--body",
            body,
            "--base",
            "main",
            "--head",
            integration_branch,
        ],
        fatal=False,
    )


def drive_milestone(milestone_title: Optional[str] = None, resume_issue: Optional[int] = None) -> None:
    if not milestone_title:
        state = load_state()
        if not state:
            print("Error: no milestone provided and no saved state found.")
            return
        milestone_title = str(state["milestone"])
        resume_issue = int(state["current_issue"])
        print(f"[Driver] Resuming milestone '{milestone_title}' from Issue #{resume_issue}.")

    print(f"=== Project Driver: {milestone_title} ===")
    issues = get_open_issues(milestone_title)
    if not issues:
        print(f"No open issues found for '{milestone_title}'.")
        clear_state()
        return

    integration_branch = detect_integration_branch(milestone_title)
    print(f"[Driver] Integration branch: {integration_branch}")
    ensure_integration_branch(integration_branch)

    start_script = script_path("project-task-start", "start.py")
    finish_script = script_path("project-task-finish", "finish.py")
    review_script = script_path("project-task-review", "review.py")
    debug_script = script_path("project-task-debugger", "debug.py")

    for issue in issues:
        issue_num = int(issue["number"])
        issue_title = str(issue["title"])

        if resume_issue and issue_num != resume_issue:
            continue
        resume_issue = None

        save_state(milestone_title, issue_num)
        ensure_integration_branch(integration_branch)

        print(f"\n--- Processing Issue #{issue_num}: {issue_title} ---")
        start_code = run_python_script(start_script, ["--issue", str(issue_num)])
        if start_code != 0:
            print(f"[Driver] project-task-start failed for Issue #{issue_num}.")
            sys.exit(start_code)

        issue_details = get_issue_details(issue_num)
        print_issue_context(issue_details)

        while True:
            print("\n[Driver] Implementation handoff")
            print(f"- Issue #{issue_num}: {issue_title}")
            print(f"- Use `project-task-implementer` and keep `{PROGRESS_FILE}` updated.")
            print("- Review should pass against Definition of done and Verification, not only compile success.")
            user_input = input("Press Enter when implementation is ready for finish/review (or 'q' to stop): ").strip().lower()
            if user_input == "q":
                sys.exit(0)

            finish_code = run_python_script(
                finish_script,
                ["--issue", str(issue_num), "--use-progress-verification", "--use-debugger"],
            )
            if finish_code != 0:
                print("[Driver] Finish failed. Check TASK_DEBUG.md or verification output, then continue implementation.")
                continue

            pr = current_pr()
            if not pr:
                print("[Driver] No open PR found for the current branch after finish.")
                continue

            review_result = run_json_script(
                review_script,
                ["--pr", str(pr["number"]), "--progress-file", PROGRESS_FILE, "--use-progress-verification", "--json"],
            )

            if review_result.get("status") != "pass":
                print_review_failures(review_result)
                failed_command = first_failed_verification(review_result)
                if failed_command:
                    print(f"[Driver] Creating debug report for failed command: {failed_command}")
                    run_python_script(debug_script, ["--command", failed_command, "--progress-file", PROGRESS_FILE])
                print("[Driver] Looping back to implementation.")
                continue

            print(f"[Driver] Review passed for PR #{pr['number']}: {pr['title']}")
            merge_input = input("Merge this PR and close the issue? (y/n): ").strip().lower()
            if merge_input != "y":
                print("[Driver] Merge postponed. Returning to implementation loop.")
                continue

            merge_pr(int(pr["number"]))
            close_issue(issue_num)
            ensure_integration_branch(integration_branch)
            update_integration_pr(integration_branch, issue_num, issue_title)
            print(f"[Driver] Issue #{issue_num} complete.")
            break

    clear_state()
    print(f"=== Project Driver complete: {milestone_title} ===")
    if integration_branch != "main":
        create_release_pr(milestone_title, integration_branch)


def main() -> None:
    parser = argparse.ArgumentParser(description="Drive milestone execution with week-issue context.")
    parser.add_argument("--milestone", type=str, help="Milestone title to drive")
    parser.add_argument("--resume", action="store_true", help="Resume from saved state")
    args = parser.parse_args()

    if args.resume and not args.milestone:
        drive_milestone()
    elif args.milestone:
        drive_milestone(args.milestone)
    else:
        state = load_state()
        if state:
            print(f"Found saved state for '{state['milestone']}'. Use --resume to continue.")
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
