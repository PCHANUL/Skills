import argparse
import os
import sys

PROGRESS_FILE = "TASK_PROGRESS.md"

def init_progress(tasks):
    """Initializes the TASK_PROGRESS.md file with the given list of tasks."""
    if os.path.exists(PROGRESS_FILE):
        overwrite = input(f"{PROGRESS_FILE} already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("Operation cancelled.")
            return

    content = "# Task Implementation Progress\n\n"
    for i, task in enumerate(tasks, 1):
        content += f"- [ ] {i}. {task.strip()}\n"
    
    with open(PROGRESS_FILE, "w") as f:
        f.write(content)
    
    print(f"Initialized {PROGRESS_FILE} with {len(tasks)} tasks.")
    print("Run `python3 .../track_progress.py list` to see tasks.")

def list_progress():
    """Reads and displays the current progress."""
    if not os.path.exists(PROGRESS_FILE):
        print(f"No progress file found ({PROGRESS_FILE}). Run `init` first.")
        return

    print("\n--- Current Progress ---")
    with open(PROGRESS_FILE, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip().startswith("- ["):
                print(line.strip())
    print("------------------------\n")
    
    # Analyze next task
    for line in lines:
        if "- [ ]" in line:
            print(f"👉 NEXT ACTION: {line.replace('- [ ]', '').strip()}")
            return
    print("✅ All tasks completed!")

def complete_task(index):
    """Marks the task at the given index (1-based) as complete."""
    if not os.path.exists(PROGRESS_FILE):
        print(f"No progress file found ({PROGRESS_FILE}).")
        return

    with open(PROGRESS_FILE, "r") as f:
        lines = f.readlines()

    new_lines = []
    found = False
    task_counter = 0
    
    for line in lines:
        if line.strip().startswith("- ["):
            task_counter += 1
            if task_counter == index:
                if "- [x]" in line:
                    print(f"Task {index} is already completed.")
                else:
                    line = line.replace("- [ ]", "- [x]")
                    print(f"✅ Marked Task {index} as completed.")
                    found = True
        new_lines.append(line)

    if not found and task_counter < index:
         print(f"Error: Task index {index} not found (Total tasks: {task_counter}).")
         return

    with open(PROGRESS_FILE, "w") as f:
        f.writelines(new_lines)

    # Show what's next
    list_progress()

def status():
    """Shows a simple percentage status."""
    if not os.path.exists(PROGRESS_FILE):
        print("No progress file.")
        return

    total = 0
    done = 0
    with open(PROGRESS_FILE, "r") as f:
        for line in f:
            if line.strip().startswith("- ["):
                total += 1
                if "- [x]" in line:
                    done += 1
    
    if total == 0:
        print("No tasks defined.")
    else:
        percent = (done / total) * 100
        print(f"Progress: {done}/{total} ({percent:.0f}%)")

def main():
    parser = argparse.ArgumentParser(description='Track task implementation progress.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Init
    init_parser = subparsers.add_parser('init', help='Initialize task list')
    init_parser.add_argument('tasks', nargs='+', help='List of tasks (strings)')

    # List
    subparsers.add_parser('list', help='Show current tasks')

    # Complete
    complete_parser = subparsers.add_parser('complete', help='Mark a task as done')
    complete_parser.add_argument('index', type=int, help='Task number to mark done')

    # Status
    subparsers.add_parser('status', help='Show progress stats')

    args = parser.parse_args()

    if args.command == 'init':
        # Join arguments into a single list if passed as separate args, or handle quoted string
        # argparse handles "Task 1" "Task 2" as a list in args.tasks
        init_progress(args.tasks)
    elif args.command == 'list':
        list_progress()
    elif args.command == 'complete':
        complete_task(args.index)
    elif args.command == 'status':
        status()

if __name__ == "__main__":
    main()
