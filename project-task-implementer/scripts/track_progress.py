import argparse
import os
import sys
from typing import Iterable, List

PROGRESS_FILE = "TASK_PROGRESS.md"
TASK_MARKER = "## Task Checklist"


def prompt_overwrite(force: bool) -> bool:
    if not os.path.exists(PROGRESS_FILE):
        return True
    if force:
        return True

    overwrite = input(f"{PROGRESS_FILE} already exists. Overwrite? (y/n): ")
    return overwrite.strip().lower() == "y"


def append_section(lines: List[str], title: str, items: Iterable[str]) -> None:
    cleaned = [item.strip() for item in items if item and item.strip()]
    if not cleaned:
        return

    lines.append(f"## {title}")
    lines.append("")
    for item in cleaned:
        lines.append(f"- {item}")
    lines.append("")


def build_progress_document(args: argparse.Namespace) -> str:
    lines: List[str] = ["# Task Implementation Progress", ""]

    issue_metadata: List[str] = []
    if args.title:
        issue_metadata.append(f"Title: {args.title.strip()}")
    if args.source:
        issue_metadata.append(f"Source: {args.source.strip()}")
    append_section(lines, "Issue", issue_metadata)

    append_section(lines, "Why this week exists", args.why)
    append_section(lines, "Read first", args.read_first)
    append_section(lines, "Current code reality", args.current_code_reality)
    append_section(lines, "Target outcome", args.target_outcome)
    append_section(lines, "Files likely touched", args.files_likely_touched)
    append_section(lines, "Out of scope", args.out_of_scope)
    append_section(lines, "Definition of done", args.definition_of_done)
    append_section(lines, "Verification", args.verification)

    lines.append(TASK_MARKER)
    lines.append("")
    for index, task in enumerate(args.tasks, 1):
        lines.append(f"- [ ] {index}. {task.strip()}")
    lines.append("")

    return "\n".join(lines)


def init_progress(args: argparse.Namespace) -> None:
    if not prompt_overwrite(args.force):
        print("Operation cancelled.")
        return

    content = build_progress_document(args)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Initialized {PROGRESS_FILE} with {len(args.tasks)} tasks.")
    if args.title:
        print(f"Issue: {args.title}")
    print("Run `python3 .../track_progress.py context` to review stored context.")


def read_progress_lines() -> List[str]:
    if not os.path.exists(PROGRESS_FILE):
        print(f"No progress file found ({PROGRESS_FILE}). Run `init` first.")
        return []

    with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
        return file.readlines()


def extract_issue_title(lines: Iterable[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- Title:"):
            return stripped.replace("- Title:", "", 1).strip()
    return ""


def task_lines(lines: Iterable[str]) -> List[str]:
    return [line.rstrip("\n") for line in lines if line.strip().startswith("- [")]


def context_lines(lines: List[str]) -> List[str]:
    output: List[str] = []
    for line in lines:
        if line.strip() == TASK_MARKER:
            break
        output.append(line.rstrip("\n"))
    return output


def next_action(lines: Iterable[str]) -> str:
    for line in lines:
        if "- [ ]" in line:
            return line.replace("- [ ]", "", 1).strip()
    return ""


def show_context() -> None:
    lines = read_progress_lines()
    if not lines:
        return

    print("\n--- Stored Context ---")
    for line in context_lines(lines):
        print(line)
    print("----------------------\n")


def list_progress() -> None:
    lines = read_progress_lines()
    if not lines:
        return

    title = extract_issue_title(lines)
    if title:
        print(f"\nIssue: {title}")
    print("--- Current Tasks ---")
    for line in task_lines(lines):
        print(line.strip())
    print("---------------------\n")

    action = next_action(lines)
    if action:
        print(f"NEXT ACTION: {action}")
    else:
        print("All tasks completed.")


def complete_task(index: int) -> None:
    lines = read_progress_lines()
    if not lines:
        return

    new_lines: List[str] = []
    found = False
    task_counter = 0

    for line in lines:
        if line.strip().startswith("- ["):
            task_counter += 1
            if task_counter == index:
                if "- [x]" in line:
                    print(f"Task {index} is already completed.")
                else:
                    line = line.replace("- [ ]", "- [x]", 1)
                    print(f"Marked Task {index} as completed.")
                    found = True
        new_lines.append(line)

    if not found and task_counter < index:
        print(f"Error: Task index {index} not found (total tasks: {task_counter}).")
        return

    with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
        file.writelines(new_lines)

    list_progress()


def status() -> None:
    lines = read_progress_lines()
    if not lines:
        return

    title = extract_issue_title(lines)
    total = 0
    done = 0
    for line in lines:
        if line.strip().startswith("- ["):
            total += 1
            if "- [x]" in line:
                done += 1

    if title:
        print(f"Issue: {title}")

    if total == 0:
        print("No tasks defined.")
        return

    percent = (done / total) * 100
    print(f"Progress: {done}/{total} ({percent:.0f}%)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track task implementation progress.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize task list")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing progress file without prompting")
    init_parser.add_argument("--title", help="Issue or task title")
    init_parser.add_argument("--source", help="Source of truth document or issue URL")
    init_parser.add_argument("--why", action="append", default=[], help="Why this task exists")
    init_parser.add_argument("--read-first", action="append", default=[], help="Reference docs to read first")
    init_parser.add_argument(
        "--current-code-reality",
        action="append",
        default=[],
        help="Current codebase state or known mismatches",
    )
    init_parser.add_argument("--target-outcome", action="append", default=[], help="Expected end state")
    init_parser.add_argument(
        "--files-likely-touched",
        action="append",
        default=[],
        help="Files or modules expected to change",
    )
    init_parser.add_argument("--out-of-scope", action="append", default=[], help="Explicitly excluded work")
    init_parser.add_argument(
        "--definition-of-done",
        action="append",
        default=[],
        help="Completion criteria that must be checked before handoff",
    )
    init_parser.add_argument(
        "--verification",
        action="append",
        default=[],
        help="Commands or checks to run before completion",
    )
    init_parser.add_argument("tasks", nargs="+", help="Implementation sub-tasks")

    subparsers.add_parser("context", help="Show stored issue context")
    subparsers.add_parser("list", help="Show current tasks")

    complete_parser = subparsers.add_parser("complete", help="Mark a task as done")
    complete_parser.add_argument("index", type=int, help="Task number to mark done")

    subparsers.add_parser("status", help="Show progress stats")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        init_progress(args)
    elif args.command == "context":
        show_context()
    elif args.command == "list":
        list_progress()
    elif args.command == "complete":
        complete_task(args.index)
    elif args.command == "status":
        status()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
