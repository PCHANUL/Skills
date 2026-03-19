import argparse
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

DEFAULT_PROGRESS_FILE = "TASK_PROGRESS.md"
DEFAULT_REPORT_FILE = "TASK_DEBUG.md"
TASK_MARKER = "## Task Checklist"


def run_command(command: str) -> Tuple[int, str, str]:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout or "", result.stderr or ""


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


def incomplete_tasks(progress: Dict[str, object]) -> List[str]:
    tasks = progress.get("tasks", [])
    if not isinstance(tasks, list):
        return []
    return [task["text"] for task in tasks if not task.get("done")]


def format_bullets(items: List[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def failure_excerpt(stdout: str, stderr: str, tail_lines: int) -> str:
    combined = stderr.strip() or stdout.strip()
    if not combined:
        return "(no output captured)"

    lines = combined.splitlines()
    return "\n".join(lines[-tail_lines:])


def build_report(
    *,
    command: str,
    progress: Dict[str, object],
    code: int,
    stdout: str,
    stderr: str,
    tail_lines: int,
) -> str:
    title = progress_title(progress) or "Unknown task"
    current_code = section_items(progress, "Current code reality")
    target = section_items(progress, "Target outcome")
    files = section_items(progress, "Files likely touched")
    done_items = section_items(progress, "Definition of done")
    verification = section_items(progress, "Verification")
    remaining = incomplete_tasks(progress)

    parts = [
        "# Task Debug Report",
        "",
        "## Failure",
        "",
        f"- Issue: {title}",
        f"- Command: `{command}`",
        f"- Exit code: {code}",
        "",
        "## Failure Excerpt",
        "",
        "```",
        failure_excerpt(stdout, stderr, tail_lines),
        "```",
        "",
        "## Current Code Reality",
        format_bullets(current_code, "No current code reality notes found."),
        "",
        "## Target Outcome",
        format_bullets(target, "No target outcome notes found."),
        "",
        "## Definition Of Done",
        format_bullets(done_items, "No definition of done notes found."),
        "",
        "## Verification",
        format_bullets(verification, "No verification steps found."),
        "",
        "## Remaining Tasks",
        format_bullets(remaining, "No incomplete tasks recorded."),
        "",
        "## Files Likely Touched",
        format_bullets(files, "No likely files recorded."),
    ]
    return "\n".join(parts)


def write_report(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def debug_loop(args: argparse.Namespace) -> int:
    progress = read_progress_file(args.progress_file)
    title = progress_title(progress)
    print(f"--- Project Task Debugger: `{args.command}` ---")
    if title:
        print(f"Issue: {title}")

    attempts = args.max_retries if args.interactive else 1

    for attempt in range(1, attempts + 1):
        print(f"\n[Attempt {attempt}/{attempts}] Running command...")
        code, stdout, stderr = run_command(args.command)

        if code == 0:
            print("Command succeeded.")
            return 0

        excerpt = failure_excerpt(stdout, stderr, args.tail_lines)
        print(f"Command failed with exit code {code}.")
        print("--- Failure Output ---")
        print(excerpt)
        print("----------------------")

        report = build_report(
            command=args.command,
            progress=progress,
            code=code,
            stdout=stdout,
            stderr=stderr,
            tail_lines=args.tail_lines,
        )
        write_report(args.report_file, report)
        print(f"Debug report written to {args.report_file}")

        if not args.interactive or attempt == attempts:
            return code

        print("Review the failure against TASK_PROGRESS.md before editing.")
        user_input = input("Press Enter after applying a fix (or 'q' to stop): ").strip().lower()
        if user_input == "q":
            print("Debugging aborted.")
            return code

    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a command with issue-aware debugging context.")
    parser.add_argument("--command", required=True, help='Command to debug, e.g. "./scripts/client_build_web.sh"')
    parser.add_argument(
        "--progress-file",
        default=DEFAULT_PROGRESS_FILE,
        help=f"Path to TASK_PROGRESS file (default: {DEFAULT_PROGRESS_FILE})",
    )
    parser.add_argument(
        "--report-file",
        default=DEFAULT_REPORT_FILE,
        help=f"Path to write debug report (default: {DEFAULT_REPORT_FILE})",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Pause between attempts so the agent can edit code and retry.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry count in interactive mode.",
    )
    parser.add_argument(
        "--tail-lines",
        type=int,
        default=20,
        help="How many lines of failure output to keep in the report.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(debug_loop(args))


if __name__ == "__main__":
    main()
