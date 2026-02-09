import argparse
import subprocess
import sys
import json
import os

def run_command(cmd_list):
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None

def get_open_issues(milestone_title):
    """
    Fetches open issues for the Milestone using gh.
    Sorts by created date (oldest first) as a simple heuristic.
    """
    cmd = [
        "gh", "issue", "list",
        "--milestone", milestone_title,
        "--state", "open",
        "--json", "number,title,state,milestone",
        "--limit", "100"
    ]
    output = run_command(cmd)
    if not output:
        return []
    return json.loads(output)

STATE_FILE = "DRIVER_STATE.json"

def save_state(milestone, issue_num):
    data = {
        "milestone": milestone,
        "current_issue": issue_num,
        "timestamp": os.path.getmtime(STATE_FILE) if os.path.exists(STATE_FILE) else 0
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f)
    print(f"[Driver] State saved: Milestone '{milestone}', Issue #{issue_num}")

def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def clear_state():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    print("[Driver] State cleared.")

def drive_milestone(milestone_title=None, resume_issue=None):
    # Auto-resume logic
    if not milestone_title:
        state = load_state()
        if state:
            print(f"[Driver] Found saved state for Milestone '{state['milestone']}'. Resuming...")
            milestone_title = state['milestone']
            resume_issue = state['current_issue']
        else:
            print("Error: No milestone provided and no saved state found.")
            return

    print(f"=== Project Driver: Starting Milestone '{milestone_title}' ===")
    
    issues = get_open_issues(milestone_title)
    if not issues:
        print(f"No open issues found for Milestone '{milestone_title}'.")
        clear_state()
        return

    print(f"Found {len(issues)} open issues.")
    
    # Parse Phase Number from Milestone Title
    import re
    phase_match = re.search(r'Phase\s+(\d+)', milestone_title, re.IGNORECASE)
    integration_branch = "main" # Fallback
    if phase_match:
        phase_num = phase_match.group(1)
        integration_branch = f"milestone/phase-{phase_num}"
        print(f"[Driver] Identified Integration Branch: {integration_branch}")
        
        # Switch to Integration Branch
        print(f"[Driver] Switching to {integration_branch}...")
        subprocess.run(["git", "fetch", "origin"], check=False)
        subprocess.run(["git", "checkout", integration_branch], check=False)
        subprocess.run(["git", "pull", "origin", integration_branch], check=False)
    
    # Process issues sequentially
    for issue in issues:
        issue_num = issue['number']
        issue_title = issue['title']
        
        # Skip until resume_issue, if provided
        if resume_issue and issue_num != resume_issue:
            continue
        resume_issue = None # Reset once found

        # Save state before processing
        save_state(milestone_title, issue_num)

        print(f"\n--- Processing Issue #{issue_num}: {issue_title} ---")
        
        # 0. Ensure we are on the latest integration branch
        subprocess.run(["git", "checkout", integration_branch], check=True)
        subprocess.run(["git", "pull", "origin", integration_branch], check=False)

        # 1. Start Task
        print(f"[Driver] Starting task {issue_num}...")
        subprocess.run(["python3", os.path.expanduser("~/Skills/project-task-start/scripts/start.py"), "--issue", str(issue_num)])
        
        # 2. IMPLEMENTATION LOOP (Includes Review Feedback)
        while True:
            print("\n" + "="*60)
            print(f"!!! ACTION REQUIRED: IMPLEMENTATION !!!")
            print(f"Issue #{issue_num} is waiting for implementation.")
            print(f"AGENT: Please use `project-task-implementer` to write/modify code.")
            print(f"If you just corrected code based on review, do it now.")
            print("="*60 + "\n")
            
            # Interactive Break: In a real run, the script stops or waits for input.
            user_input = input("Press Enter when implementation is done (or 'q' to quit): ")
            if user_input.lower() == 'q':
                sys.exit(0)

            # 3. Finish Task (Create/Update PR)
            print(f"[Driver] Finishing task {issue_num} (Committing & Pushing)...")
            subprocess.run(["python3", os.path.expanduser("~/Skills/project-task-finish/scripts/finish.py"), "--issue", str(issue_num)])
            
            # 3a. Update PR base to integration branch (if available)
            if integration_branch != "main":
                try:
                    # Get current branch name
                    current_branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
                    print(f"[Driver] Updating PR base to {integration_branch}...")
                    subprocess.run(["gh", "pr", "edit", current_branch, "--base", integration_branch], check=False)
                except Exception as e:
                    print(f"Warning: Failed to update PR base: {e}")

            # 4. REVIEW KICKOFF
            print(f"[Driver] Structuring `project-task-review`...")
            
            print("\n" + "*"*60)
            print("Please run `project-task-review` check now.")
            review_status = input("Did the PR pass review? (y/n, n = request changes): ")
            
            if review_status.lower() == 'y':
                print(f"Review Passed! Merging PR into {integration_branch}...")
                
                # Merge PR
                # --delete-branch cleans up the feature branch
                merge_cmd = ["gh", "pr", "merge", "--merge", "--delete-branch"]
                subprocess.run(merge_cmd, check=False)
                
                # Update local integration branch
                subprocess.run(["git", "checkout", integration_branch], check=False)
                subprocess.run(["git", "pull", "origin", integration_branch], check=False)
                
                break  # Exit loop to next issue
            else:
                print("Review Failed. Looping back to implementation...")
                # Continue while loop
        
        print(f"Issue #{issue_num} cycle complete.")
    
    # Cleanup state after milestone completion
    clear_state()
    print(f"=== Project Driver: Milestone '{milestone_title}' Complete! ===")

def main():
    parser = argparse.ArgumentParser(description='Project Driver: Automate Task Execution Cycle')
    parser.add_argument('--milestone', type=str, help='Title of the Milestone to drive')
    parser.add_argument('--resume', action='store_true', help='Resume from saved state')
    
    args = parser.parse_args()
    
    if args.resume and not args.milestone:
        drive_milestone() # Auto-resume
    elif args.milestone:
        drive_milestone(args.milestone)
    else:
        # Try auto-resume default or show help
        state = load_state()
        if state:
            print(f"Found saved state for '{state['milestone']}'. Use --resume to continue.")
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
