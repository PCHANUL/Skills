import argparse
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

DEFAULT_PROGRESS_FILE = "TASK_PROGRESS.md"
TASK_MARKER = "## Task Checklist"


def run_command(cmd_list: List[str], check: bool = True) -> Optional[str]:
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.strip() if error.stderr else ""
        if check:
            print(f"Error running command: {' '.join(cmd_list)}")
            if stderr:
                print(stderr)
        return None


def run_shell(command: str) -> Tuple[bool, str]:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
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


def progress_title(progress: Dict[str, object]) -> str:
    for item in section_items(progress, "Issue"):
        if item.startswith("Title:"):
            return item.replace("Title:", "", 1).strip()
    return ""


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


def changed_files_for_pr(pr_number: Optional[int]) -> List[str]:
    if pr_number:
        output = run_command(
            ["gh", "pr", "view", str(pr_number), "--json", "files", "--jq", ".files[].path"],
            check=False,
        )
        if not output:
            return []
        return [line for line in output.splitlines() if line.strip()]

    output = run_command(["git", "diff", "--name-only", "HEAD"], check=False)
    if not output:
        return []
    return [line for line in output.splitlines() if line.strip()]


def run_verifications(commands: List[str]) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    for command in commands:
        ok, output = run_shell(command)
        results.append(
            {
                "command": command,
                "status": "passed" if ok else "failed",
                "output": output,
            }
        )
        if not ok:
            break
    return results


def build_result(
    progress: Dict[str, object],
    changed_files: List[str],
    verification_results: List[Dict[str, str]],
) -> Dict[str, object]:
    remaining = incomplete_tasks(progress)
    verification_failed = any(item["status"] != "passed" for item in verification_results)
    status = "pass"
    if remaining or verification_failed:
        status = "fail"

    return {
        "status": status,
        "issue_title": progress_title(progress),
        "target_outcome": section_items(progress, "Target outcome"),
        "definition_of_done": section_items(progress, "Definition of done"),
        "changed_files": changed_files,
        "completed_tasks": completed_tasks(progress),
        "incomplete_tasks": remaining,
        "verification_results": verification_results,
    }


def print_human_summary(result: Dict[str, object]) -> None:
    print("--- Project Task Review ---")
    if result.get("issue_title"):
        print(f"Issue: {result['issue_title']}")
    print(f"Result: {str(result.get('status', 'unknown')).upper()}")

    changed_files = result.get("changed_files", [])
    if changed_files:
        print("Changed files:")
        for path in changed_files:
            print(f"- {path}")

    incomplete = result.get("incomplete_tasks", [])
    if incomplete:
        print("Incomplete tasks:")
        for task in incomplete:
            print(f"- {task}")

    verification = result.get("verification_results", [])
    if verification:
        print("Verification:")
        for item in verification:
            print(f"- {item['command']}: {item['status']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Review task completion against TASK_PROGRESS.md.")
    parser.add_argument("--pr", type=int, help="PR number to review")
    parser.add_argument(
        "--progress-file",
        default=DEFAULT_PROGRESS_FILE,
        help=f"Path to progress file (default: {DEFAULT_PROGRESS_FILE})",
    )
    parser.add_argument(
        "--verification-cmd",
        action="append",
        default=[],
        help="Verification command to run. Can be passed multiple times.",
    )
    parser.add_argument(
        "--use-progress-verification",
        action="store_true",
        help="Run commands listed in the progress file Verification section.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    args = parser.parse_args()

    progress = read_progress_file(args.progress_file)
    changed_files = changed_files_for_pr(args.pr)

    verification_commands = list(args.verification_cmd or [])
    if args.use_progress_verification:
        verification_commands.extend(section_items(progress, "Verification"))

    verification_results = run_verifications(verification_commands)
    result = build_result(progress, changed_files, verification_results)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human_summary(result)

    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
