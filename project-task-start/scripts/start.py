import argparse
import re
import subprocess
import sys

def run_command(cmd_list, check=True):
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd_list)}\n{e.stderr}")
        if check:
            sys.exit(1)
        return None

def get_issue_title(issue_num):
    """Fetches issue title using gh CLI."""
    print(f"Fetching title for Issue #{issue_num}...")
    title = run_command(["gh", "issue", "view", str(issue_num), "--json", "title", "--jq", ".title"])
    return title

def sanitize_branch_name(title):
    """Converts title to a valid branch name suffix."""
    # "Implement Login Feature" -> "implement-login-feature"
    name = re.sub(r'[^\w\s-]', '', title).strip().lower()
    name = re.sub(r'[\s]+', '-', name)
    return name

def start_task(issue_num):
    title = get_issue_title(issue_num)
    if not title:
        print(f"Could not find issue #{issue_num}")
        sys.exit(1)
        
    safe_title = sanitize_branch_name(title)
    branch_name = f"feat/issue-{issue_num}-{safe_title}"
    
    # Check if branch exists
    print(f"Checking for branch '{branch_name}'...")
    exists = run_command(["git", "rev-parse", "--verify", branch_name], check=False)
    
    if exists:
        print(f"Branch '{branch_name}' already exists. Checking out...")
        run_command(["git", "checkout", branch_name])
    else:
        print(f"Creating new branch '{branch_name}'...")
        run_command(["git", "checkout", "-b", branch_name])
        
        # Assign self to issue and set label to in-progress
        print("Updating issue status...")
        run_command(["gh", "issue", "edit", str(issue_num), "--add-assignee", "@me", "--add-label", "in-progress"], check=False)

    print(f"\n✅ Task #{issue_num} Started!")
    print(f"   Branch: {branch_name}")
    print(f"   Issue: {title}")

def main():
    parser = argparse.ArgumentParser(description='Start working on a GitHub Issue.')
    parser.add_argument('--issue', type=int, required=True, help='Issue number to start')
    args = parser.parse_args()
    
    start_task(args.issue)

if __name__ == "__main__":
    main()
