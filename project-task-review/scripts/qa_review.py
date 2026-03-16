import argparse
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional

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


def fetch_changed_files(pr_number: int) -> List[str]:
    output = run_command(["gh", "pr", "view", str(pr_number), "--json", "files", "--jq", ".files[].path"], check=False)
    if not output:
        return []
    return [line for line in output.splitlines() if line.strip()]


def fetch_full_content(file_path: str) -> str:
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except OSError as error:
        return f"[Error reading file: {error}]"


def build_bundle(pr_number: int, progress: Dict[str, object], changed_files: List[str]) -> str:
    title = progress_title(progress) or f"PR #{pr_number}"
    parts: List[str] = [
        f"# Review Context For PR #{pr_number}",
        "",
        f"Issue: {title}",
        "",
        "## Target Outcome",
    ]

    target = section_items(progress, "Target outcome")
    if target:
        parts.extend(f"- {item}" for item in target)
    else:
        parts.append("- No target outcome recorded.")

    parts.extend(["", "## Current Code Reality"])
    current = section_items(progress, "Current code reality")
    if current:
        parts.extend(f"- {item}" for item in current)
    else:
        parts.append("- No current code reality recorded.")

    parts.extend(["", "## Definition Of Done"])
    done_items = section_items(progress, "Definition of done")
    if done_items:
        parts.extend(f"- {item}" for item in done_items)
    else:
        parts.append("- No definition of done recorded.")

    parts.extend(["", "## Verification"])
    verification = section_items(progress, "Verification")
    if verification:
        parts.extend(f"- {item}" for item in verification)
    else:
        parts.append("- No verification steps recorded.")

    parts.extend(["", "## Changed Files"])
    if changed_files:
        parts.extend(f"- {path}" for path in changed_files)
    else:
        parts.append("- No changed files found.")

    for path in changed_files:
        if path.endswith((".png", ".jpg", ".jpeg", ".gif", ".lock", ".resolved")):
            continue
        content = fetch_full_content(path)
        parts.extend(
            [
                "",
                f"## File: {path}",
                "```",
                content,
                "```",
            ]
        )

    parts.extend(
        [
            "",
            "## Review Questions",
            "1. Does the implementation match the target outcome?",
            "2. Does the diff actually satisfy the definition of done?",
            "3. Are there gaps between the changed files and the remaining code reality mismatches?",
            "4. Are the required verification steps reflected in the implementation and PR state?",
            "5. Is there any scope leakage or regression outside the week boundary?",
        ]
    )

    return "\n".join(parts)


def analyze_pr(pr_number: int, progress_file: str) -> None:
    progress = read_progress_file(progress_file)
    changed_files = fetch_changed_files(pr_number)
    bundle = build_bundle(pr_number, progress, changed_files)

    print("=" * 60)
    print("READY FOR AGENT REVIEW")
    print("=" * 60)
    print(bundle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a deep review context bundle for a PR.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Prepare review context for a PR")
    analyze_parser.add_argument("--pr", type=int, required=True, help="PR number")
    analyze_parser.add_argument(
        "--progress-file",
        default=DEFAULT_PROGRESS_FILE,
        help=f"Path to progress file (default: {DEFAULT_PROGRESS_FILE})",
    )

    args = parser.parse_args()

    if args.command == "analyze":
        analyze_pr(args.pr, args.progress_file)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
