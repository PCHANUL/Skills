import argparse
import json
import re
import subprocess
import sys
from typing import Dict, List, Optional

CONTEXT_HEADINGS = [
    "Read first",
    "Current code reality",
    "Target outcome",
    "Definition of done",
    "Verification",
]


def run_command(cmd_list: List[str], check: bool = True) -> Optional[str]:
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.strip() if error.stderr else ""
        print(f"Error running command: {' '.join(cmd_list)}")
        if stderr:
            print(stderr)
        if check:
            sys.exit(1)
        return None


def issue_details(issue_num: int) -> Dict[str, object]:
    output = run_command(
        ["gh", "issue", "view", str(issue_num), "--json", "title,body,milestone"],
        check=False,
    )
    if not output:
        print(f"Could not fetch issue #{issue_num}")
        sys.exit(1)
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


def base_branch_for_milestone(milestone_title: str) -> str:
    match = re.search(r"Phase\s+(\d+)", milestone_title, re.IGNORECASE)
    if match:
        return f"milestone/phase-{match.group(1)}"
    return "main"


def ensure_branch(branch_name: str) -> None:
    run_command(["git", "fetch", "origin"], check=False)
    remote_exists = run_command(["git", "ls-remote", "--heads", "origin", branch_name], check=False)

    local_exists = run_command(["git", "rev-parse", "--verify", branch_name], check=False)
    if local_exists:
        run_command(["git", "checkout", branch_name])
        if remote_exists:
            run_command(["git", "pull", "origin", branch_name], check=False)
        return

    if remote_exists:
        run_command(["git", "checkout", "-b", branch_name, "--track", f"origin/{branch_name}"])
        return

    run_command(["git", "checkout", "-b", branch_name])


def create_or_restore_feature_branch(issue_num: int, base_branch: str) -> str:
    branch_name = f"feat/issue-{issue_num}"
    print(f"Preparing base branch `{base_branch}`...")
    ensure_branch(base_branch)

    print(f"Preparing feature branch `{branch_name}`...")
    feature_exists = run_command(["git", "rev-parse", "--verify", branch_name], check=False)
    if feature_exists:
        run_command(["git", "checkout", branch_name])
        return branch_name

    remote_exists = run_command(["git", "ls-remote", "--heads", "origin", branch_name], check=False)
    if remote_exists:
        run_command(["git", "checkout", "-b", branch_name, "--track", f"origin/{branch_name}"])
        return branch_name

    run_command(["git", "checkout", "-b", branch_name, base_branch])
    return branch_name


def update_issue_status(issue_num: int) -> None:
    run_command(
        ["gh", "issue", "edit", str(issue_num), "--add-assignee", "@me", "--add-label", "in-progress"],
        check=False,
    )


def print_context(title: str, milestone: str, branch_name: str, sections: Dict[str, List[str]]) -> None:
    print("\nTask started.")
    print(f"Issue: {title}")
    print(f"Milestone: {milestone}")
    print(f"Branch: {branch_name}")

    for heading in CONTEXT_HEADINGS:
        values = sections.get(heading, [])
        if not values:
            continue
        print(f"\n{heading}:")
        for value in values[:8]:
            print(value)

    print("\nNext step: initialize `TASK_PROGRESS.md` with `project-task-implementer` before coding.")


def start_task(issue_num: int) -> None:
    issue = issue_details(issue_num)
    title = str(issue.get("title") or f"Issue #{issue_num}")
    body = str(issue.get("body") or "")

    milestone_info = issue.get("milestone") or {}
    milestone_title = "No milestone"
    if isinstance(milestone_info, dict) and milestone_info.get("title"):
        milestone_title = str(milestone_info["title"])

    base_branch = base_branch_for_milestone(milestone_title)
    branch_name = create_or_restore_feature_branch(issue_num, base_branch)
    update_issue_status(issue_num)
    sections = extract_context_sections(body)
    print_context(title, milestone_title, branch_name, sections)


def main() -> None:
    parser = argparse.ArgumentParser(description="Start working on a GitHub issue with week-issue context.")
    parser.add_argument("--issue", type=int, required=True, help="Issue number to start")
    args = parser.parse_args()
    start_task(args.issue)


if __name__ == "__main__":
    main()
