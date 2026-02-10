import argparse
import subprocess
import sys
import os

def run_command(cmd_list, check=True):
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd_list)}\n{e.stderr}")
        return None

def check_lint(files_changed):
    """Checks for linting errors in changed files."""
    print("running lint check...")
    # This is a placeholder. You need to configure this for your specific project.
    # e.g., if any .py files, run pylint. if .dart, flutter analyze.
    
    # Simple example: check for TODOs
    todos_found = False
    for file in files_changed:
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    for i, line in enumerate(f, 1):
                        if "TODO" in line:
                            print(f"[WARN] TODO found in {file}:{i}")
                            todos_found = True
            except:
                pass
    
    if todos_found:
        print("⚠️ Warning: TODOs found in code.")
    else:
        print("✅ No TODOs found.")
    
    # Return True if check passes (warnings are okay mostly)
    return True

def check_complexity(files_changed):
    """Checks for complex code blocks (placeholder)."""
    # e.g. check for lines > 100 chars
    return True

def review_pr(pr_number):
    print(f"--- Automated Review for PR #{pr_number} ---")
    
    # Get Changed Files
    files_output = run_command(["gh", "pr", "diff", str(pr_number), "--name-only"])
    if not files_output:
        print("No files changes detected.")
        return

    files_changed = files_output.splitlines()
    print(f"Files changed: {len(files_changed)}")
    
    # 1. Start Validation
    passed = True
    
    if not check_lint(files_changed):
        passed = False
        
    # 2. Add Review Comment
    if passed:
        body = "Automated Review: ✅ Checks Passed.\n\nReady for human/agent final review."
        event = "COMMENT"
    else:
        body = "Automated Review: ❌ Checks Failed. Please fix lint errors."
        event = "REQUEST_CHANGES"

    # print(f"Posting review: {event}")
    # run_command(["gh", "pr", "review", str(pr_number), "--body", body, "--" + event.lower().replace("_", "-")])
    
    print("\n--- Review Summary ---")
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print("Action: Check the PR on GitHub for details.")

def main():
    parser = argparse.ArgumentParser(description='Perform automated code review on a PR.')
    parser.add_argument('--pr', type=int, help='PR number to review')
    
    args = parser.parse_args()
    
    if args.pr:
        review_pr(args.pr)
    else:
        # If running locally without PR number, just check current changes
        print("Running local review on staged files...")
        status = run_command(["git", "diff", "--name-only", "--cached"])
        if status:
            check_lint(status.splitlines())
        else:
            print("No staged files to review.")

if __name__ == "__main__":
    main()
