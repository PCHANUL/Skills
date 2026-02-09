import argparse
import re
import subprocess
import sys
import time

def run_gh_command(command_list):
    """Runs a gh CLI command and returns the output."""
    try:
        result = subprocess.run(command_list, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command_list)}: {e.stderr}")
        return None

def parse_markdown(file_path):
    """Parses the task list markdown file into a structured dictionary."""
    phases = []
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        sys.exit(1)

    current_phase = None
    current_week = None
    
    for line in lines:
        line = line.strip()
        
        # Match Phase: "## 📋 Phase 1: Phase Name (Week 1-4)"
        phase_match = re.match(r'^##\s+.*?Phase\s+(\d+):\s+(.*)', line)
        if phase_match:
            if current_phase:
                phases.append(current_phase)
            
            phase_num = phase_match.group(1)
            phase_title = phase_match.group(2)
            current_phase = {
                'number': phase_num,
                'title': f"Phase {phase_num}: {phase_title}",
                'weeks': []
            }
            current_week = None
            continue
            
        # Match Week: "### Week 1: Week Goal"
        week_match = re.match(r'^###\s+Week\s+(\d+):\s+(.*)', line)
        if week_match:
            if current_phase:
                week_num = week_match.group(1)
                week_goal = week_match.group(2)
                current_week = {
                    'number': week_num,
                    'title': f"Week {week_num}: {week_goal}",
                    'body': f"# Week {week_num} Tasks\n\n"
                }
                current_phase['weeks'].append(current_week)
            continue
            
        # Append content to current week's issue body
        if current_week:
            # Preserve checkboxes and basic formatting
            if line.startswith("- [ ]") or line.startswith("- [x]"):
                current_week['body'] += line + "\n"
            elif line.startswith("####"):
                # Convert sub-headers to bold text in issue body
                current_week['body'] += f"\n**{line.replace('#', '').strip()}**\n"
            elif line:
                current_week['body'] += line + "\n"

    if current_phase:
        phases.append(current_phase)
        
    return phases

def sync_to_github(phases, repo):
    """Creates Milestones and Issues in GitHub."""
    print(f"Syncing to repository: {repo}...")
    
    for phase in phases:
        # Create Milestone
        print(f"Creating Milestone: {phase['title']}")
        milestone_cmd = [
            "gh", "api", f"repos/{repo}/milestones",
            "-f", f"title={phase['title']}",
            "--jq", ".number"
        ]
        milestone_number = run_gh_command(milestone_cmd)
        
        if not milestone_number:
            print(f"Skipping issues for {phase['title']} due to milestone error.")
            continue
            
        print(f"  > Created Milestone #{milestone_number}")
        
        # Create Issues for each week in this phase
        for week in phase['weeks']:
            print(f"  Creating Issue: {week['title']}")
            issue_cmd = [
                "gh", "issue", "create",
                "--repo", repo,
                "--title", week['title'],
                "--body", week['body'],
                "--milestone", phase['title'], # gh issue create uses title for milestone
                "--label", "enhancement"
            ]
            
            # Note: gh issue create might fail if milestone title is duplicate or not found immediately.
            # Using API is safer for IDs, but CLI is easier. relying on title match.
            issue_url = run_gh_command(issue_cmd)
            if issue_url:
                 print(f"    > Created Issue: {issue_url}")
            
            # Rate limiting pause
            time.sleep(1)

        # Create Milestone Branch (Integration Branch)
        # Format: milestone/phase-N
        branch_name = f"milestone/phase-{phase['number']}"
        print(f"Creating Integration Branch: {branch_name} from main...")
        
        # Get main branch SHA
        sha_cmd = ["gh", "api", f"repos/{repo}/git/ref/heads/main", "--jq", ".object.sha"]
        main_sha = run_gh_command(sha_cmd)
        
        if main_sha:
            # Create ref
            create_ref_cmd = [
                "gh", "api", f"repos/{repo}/git/refs",
                "-f", f"ref=refs/heads/{branch_name}",
                "-f", f"sha={main_sha}"
            ]
            run_gh_command(create_ref_cmd)
            print(f"  > Created Remote Branch: {branch_name}")
        else:
            print("  > Failed to get main SHA. Skipping branch creation.")

def main():
    parser = argparse.ArgumentParser(description='Sync task list to GitHub Milestones and Issues.')
    parser.add_argument('--file', type=str, required=True, help='Path to the task list markdown file.')
    parser.add_argument('--repo', type=str, required=True, help='Target GitHub repository (owner/repo).')
    
    args = parser.parse_args()
    
    phases = parse_markdown(args.file)
    if not phases:
        print("No phases found in the markdown file. Check format.")
        return

    sync_to_github(phases, args.repo)

if __name__ == "__main__":
    main()
