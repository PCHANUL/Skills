import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Dict, List, Optional


def run_gh_command(command_list: List[str], check: bool = True) -> Optional[str]:
    """Run a gh command and return stdout."""
    result = subprocess.run(command_list, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command {' '.join(command_list)}:\n{result.stderr}")
        raise RuntimeError(result.stderr.strip())
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def run_gh_json(command_list: List[str]):
    output = run_gh_command(command_list)
    return json.loads(output) if output else None


def parse_markdown(file_path: str):
    """Parse a project todo markdown file into phases and issue-ready week sections."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        sys.exit(1)

    phase_pattern = re.compile(r"^##\s+.*?Phase\s+(\d+):\s+(.*)$", re.M)
    week_pattern = re.compile(r"^###\s+Week\s+(\d+):\s+(.*)$", re.M)

    phases = []
    phase_matches = list(phase_pattern.finditer(text))
    if not phase_matches:
        return phases

    for i, phase_match in enumerate(phase_matches):
        phase_start = phase_match.start()
        phase_end = phase_matches[i + 1].start() if i + 1 < len(phase_matches) else len(text)
        phase_block = text[phase_start:phase_end]
        phase_num = phase_match.group(1)
        phase_title = phase_match.group(2).strip()

        phase = {
            "number": phase_num,
            "title": f"Phase {phase_num}: {phase_title}",
            "weeks": [],
        }

        week_matches = list(week_pattern.finditer(phase_block))
        for j, week_match in enumerate(week_matches):
            block_start = week_match.start()
            block_end = week_matches[j + 1].start() if j + 1 < len(week_matches) else len(phase_block)
            week_block = phase_block[block_start:block_end].strip()
            week_num = week_match.group(1)
            week_goal = week_match.group(2).strip()
            body = f"Source of truth: `{file_path}`\n\n{week_block}\n"
            phase["weeks"].append(
                {
                    "number": week_num,
                    "title": f"Week {week_num}: {week_goal}",
                    "body": body,
                }
            )

        phases.append(phase)

    return phases


def get_existing_milestones(repo: str) -> Dict[str, dict]:
    milestones = run_gh_json(["gh", "api", f"repos/{repo}/milestones?state=all&per_page=100"]) or []
    return {milestone["title"]: milestone for milestone in milestones}


def ensure_milestone(repo: str, title: str) -> dict:
    existing = get_existing_milestones(repo)
    if title in existing:
        print(f"Reusing Milestone: {title}")
        return existing[title]

    print(f"Creating Milestone: {title}")
    milestone = run_gh_json(["gh", "api", f"repos/{repo}/milestones", "-f", f"title={title}"])
    print(f"  > Created Milestone #{milestone['number']}")
    return milestone


def get_existing_issues(repo: str) -> Dict[str, dict]:
    issues = run_gh_json(["gh", "api", f"repos/{repo}/issues?state=all&per_page=200"]) or []
    issue_map = {}
    for issue in issues:
        if "pull_request" in issue:
            continue
        issue_map[issue["title"]] = issue
    return issue_map


def upsert_issue(repo: str, title: str, body: str, milestone_title: str):
    issues = get_existing_issues(repo)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
        tmp.write(body)
        tmp_path = tmp.name

    try:
        if title in issues:
            issue_number = str(issues[title]["number"])
            print(f"Updating Issue: {title}")
            run_gh_command(
                [
                    "gh",
                    "issue",
                    "edit",
                    issue_number,
                    "--repo",
                    repo,
                    "--body-file",
                    tmp_path,
                    "--milestone",
                    milestone_title,
                    "--add-label",
                    "enhancement",
                ]
            )
            print(f"  > Updated Issue #{issue_number}")
            return

        print(f"Creating Issue: {title}")
        issue_url = run_gh_command(
            [
                "gh",
                "issue",
                "create",
                "--repo",
                repo,
                "--title",
                title,
                "--body-file",
                tmp_path,
                "--milestone",
                milestone_title,
                "--label",
                "enhancement",
            ]
        )
        if issue_url:
            print(f"  > Created Issue: {issue_url}")
    finally:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass


def branch_exists(repo: str, branch_name: str) -> bool:
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/git/ref/heads/{branch_name}"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def ensure_branch(repo: str, phase_number: str) -> str:
    branch_name = f"milestone/phase-{phase_number}"
    if branch_exists(repo, branch_name):
        print(f"Reusing Integration Branch: {branch_name}")
        return branch_name

    print(f"Creating Integration Branch: {branch_name} from main...")
    main_sha = run_gh_command(["gh", "api", f"repos/{repo}/git/ref/heads/main", "--jq", ".object.sha"])
    tree_sha = run_gh_command(["gh", "api", f"repos/{repo}/git/commits/{main_sha}", "--jq", ".tree.sha"])
    new_commit_sha = run_gh_command(
        [
            "gh",
            "api",
            f"repos/{repo}/git/commits",
            "-f",
            f"message=chore: start milestone phase-{phase_number}",
            "-f",
            f"tree={tree_sha}",
            "-f",
            f"parents[]={main_sha}",
            "--jq",
            ".sha",
        ]
    )
    run_gh_command(
        [
            "gh",
            "api",
            f"repos/{repo}/git/refs",
            "-f",
            f"ref=refs/heads/{branch_name}",
            "-f",
            f"sha={new_commit_sha}",
        ]
    )
    print(f"  > Created Remote Branch: {branch_name}")
    return branch_name


def get_existing_prs(repo: str) -> List[dict]:
    return run_gh_json(["gh", "api", f"repos/{repo}/pulls?state=all&per_page=200"]) or []


def ensure_integration_pr(repo: str, phase_title: str, branch_name: str):
    pr_title = f"[{phase_title}] Integration PR"
    for pr in get_existing_prs(repo):
        if pr.get("title") == pr_title or pr.get("head", {}).get("ref") == branch_name:
            print(f"Reusing Pull Request: {pr_title}")
            return pr

    print(f"Creating Pull Request for {branch_name}...")
    pr_body = (
        f"Integration PR for **{phase_title}**.\n"
        "All related feature branches for this milestone will be merged into this phase branch before a final release to `main`."
    )
    pr_url = run_gh_command(
        [
            "gh",
            "pr",
            "create",
            "--repo",
            repo,
            "--base",
            "main",
            "--head",
            branch_name,
            "--title",
            pr_title,
            "--body",
            pr_body,
            "--milestone",
            phase_title,
        ],
        check=False,
    )
    if pr_url:
        print(f"  > Created PR: {pr_url}")
    else:
        print(f"  > PR not created for {branch_name}. This can happen when no diff exists against main.")
    return pr_url


def sync_to_github(phases, repo: str):
    print(f"Syncing to repository: {repo}...")

    for phase in phases:
        milestone = ensure_milestone(repo, phase["title"])

        for week in phase["weeks"]:
            upsert_issue(repo, week["title"], week["body"], milestone["title"])

        branch_name = ensure_branch(repo, phase["number"])
        ensure_integration_pr(repo, phase["title"], branch_name)


def main():
    parser = argparse.ArgumentParser(description="Sync task list to GitHub milestones and issues.")
    parser.add_argument("--file", type=str, required=True, help="Path to the task list markdown file.")
    parser.add_argument("--repo", type=str, required=True, help="Target GitHub repository (owner/repo).")
    args = parser.parse_args()

    phases = parse_markdown(args.file)
    if not phases:
        print("No phases found in the markdown file. Check format.")
        return

    sync_to_github(phases, args.repo)


if __name__ == "__main__":
    main()
