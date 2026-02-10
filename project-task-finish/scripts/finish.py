import argparse
import subprocess
import sys
import json

def run_command(cmd_list, check=True):
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd_list)}\n{e.stderr}")
        if check:
            sys.exit(1)
        return None

def check_existing_pr():
    """Checks if a PR is already open for the current branch."""
    current_branch = run_command(["git", "branch", "--show-current"])
    print(f"Checking for existing PR on {current_branch}...")
    
    # gh pr list --head <branch> --json url,number,state
    output = run_command(["gh", "pr", "list", "--head", current_branch, "--json", "url,number,state"], check=False)
    
    if output:
        prs = json.loads(output)
        if prs:
            pr = prs[0]
            print(f"✅ Existing PR found: #{pr['number']} ({pr['state']})")
            print(f"   URL: {pr['url']}")
            return pr['url']
    return None

def finish_task(issue_num, test_cmd=None):
    # 1. Run Tests (Optional but recommended)
    if test_cmd:
        print(f"Running tests with debugger: {test_cmd}")
        
        # Calculate relative path to debugger script
        # Current: .../project-task-finish/scripts/finish.py
        # Target:  .../project-task-debugger/scripts/debug.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        skills_root = os.path.dirname(os.path.dirname(current_dir)) # Up 2 levels
        debugger_script = os.path.join(skills_root, "project-task-debugger", "scripts", "debug.py")
        
        if not os.path.exists(debugger_script):
            print(f"⚠️ Debugger script not found at {debugger_script}. Falling back to direct execution.")
            subprocess.run(test_cmd, shell=True, check=True)
            return

        # We need to construct the command properly, passing the test command as an argument
        import shlex
        
        result = subprocess.run(
            ["python3", debugger_script, "--command", test_cmd],
            check=False
        )
        
        if result.returncode != 0:
            print("❌ Tests failed even after debugging attempts. Aborting Finish.")
            sys.exit(1)
        else:
            print("✅ Tests passed.")
    
    # 2. Add & Commit
    print("Committing changes...")
    run_command(["git", "add", "."])
    
    status = run_command(["git", "status", "--porcelain"])
    if not status:
        print("No changes to commit.")
    else:
        commit_msg = f"feat: Implement Issue #{issue_num}"
        run_command(["git", "commit", "-m", commit_msg], check=False)

    # 3. Push
    current_branch = run_command(["git", "branch", "--show-current"])
    print(f"Pushing {current_branch}...")
    run_command(["git", "push", "-u", "origin", current_branch], check=False)

    # 4. Create PR (Idempotent)
    existing_pr = check_existing_pr()
    
    if existing_pr:
        print("PR already exists. Promoting to review ready...")
        # Optional: Remove Draft status if needed. `gh pr ready`
    else:
        print("Creating new PR...")
        # Get Issue Title to use as PR title
        title = run_command(["gh", "issue", "view", str(issue_num), "--json", "title", "--jq", ".title"])
        body = f"Closes #{issue_num}\n\n## Implementation Details\n- Implemented feature as per requirements."
        
        # Determine Base Branch from Milestone
        milestone = run_command(["gh", "issue", "view", str(issue_num), "--json", "milestone", "--jq", ".milestone.title"])
        base_branch = "main"
        
        if milestone:
            import re
            match = re.search(r'Phase\s+(\d+)', milestone, re.IGNORECASE)
            if match:
                base_branch = f"milestone/phase-{match.group(1)}"
                print(f"Detected Integation Branch from Milestone '{milestone}': {base_branch}")
            else:
                print(f"Warning: Could not parse phase from milestone '{milestone}'. Defaulting to main.")
        
        # Create PR
        pr_cmd = [
            "gh", "pr", "create",
            "--title", title,
            "--body", body,
            "--base", base_branch
        ]
        
        # Add labels if possible
        # pr_cmd.extend(["--label", "needs-review"])
        
        pr_url = run_command(pr_cmd)
        print(f"✅ PR Created: {pr_url}")

def main():
    parser = argparse.ArgumentParser(description='Finish a task by committing and creating a PR.')
    parser.add_argument('--issue', type=int, required=True, help='Issue number being finished')
    parser.add_argument('--test-cmd', type=str, help='Command to run tests (e.g., "npm test")')
    
    args = parser.parse_args()
    
    finish_task(args.issue, args.test_cmd)

if __name__ == "__main__":
    main()
