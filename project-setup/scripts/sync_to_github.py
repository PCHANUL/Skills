import argparse
import re
import subprocess
import sys
import time
from typing import Dict, List, Optional


def run_gh_command(command_list: List[str]) -> Optional[str]:
    """Runs a gh CLI command and returns stdout; returns None on failure."""
    try:
        result = subprocess.run(command_list, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        err = (e.stderr or "").strip()
        print(f"Error running command {' '.join(command_list)}: {err}")
        return None


def _normalized_heading(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _extract_doc_refs(lines: List[str]) -> List[str]:
    refs = set()
    for line in lines:
        for match in re.findall(r"docs/[A-Za-z0-9_./\-]+\.md", line):
            refs.add(match)
    return sorted(refs)


def _extract_command_lines(lines: List[str]) -> List[str]:
    cmds: List[str] = []
    patterns = [r"\bflutter analyze\b", r"\bflutter test\b", r"\bdart test\b"]
    for line in lines:
        stripped = line.strip()
        if any(re.search(p, stripped) for p in patterns):
            if stripped not in cmds:
                cmds.append(stripped)
    return cmds


def _parse_week_sections(raw_lines: List[str]) -> Dict[str, List]:
    sections = {
        "categories": [],
        "files": [],
        "dod": [],
        "verification": [],
        "risks": [],
        "misc": [],
    }

    current_category = None
    current_section = "misc"
    in_code_block = False

    for raw in raw_lines:
        line = raw.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            if current_section == "verification":
                sections["verification"].append(stripped)
            elif current_category is not None:
                current_category["lines"].append(stripped)
            else:
                sections["misc"].append(stripped)
            continue

        if not stripped:
            if current_section == "verification":
                sections["verification"].append("")
            elif current_category is not None:
                current_category["lines"].append("")
            continue

        if not in_code_block:
            # H4 category header
            h4_match = re.match(r"^####\s+(.+)$", stripped)
            if h4_match:
                title = h4_match.group(1).strip()
                current_category = {"title": title, "lines": []}
                sections["categories"].append(current_category)
                current_section = "category"
                continue

            # Bold section header (e.g., **Files likely touched**)
            bold_match = re.match(r"^\*\*(.+?)\*\*:?\s*$", stripped)
            if bold_match:
                heading = _normalized_heading(bold_match.group(1))
                if "files likely touched" in heading or "likely touched" in heading or "관련 파일" in heading:
                    current_section = "files"
                    current_category = None
                    continue
                if "definition of done" in heading or "완료 기준" in heading or "definition" in heading:
                    current_section = "dod"
                    current_category = None
                    continue
                if "verification" in heading or "검증" in heading:
                    current_section = "verification"
                    current_category = None
                    continue
                if "risk" in heading or "주의" in heading:
                    current_section = "risks"
                    current_category = None
                    continue

                # Convert numeric bold sections to categories (e.g., **1.1 ...**)
                if re.match(r"^\d+\.\d+", bold_match.group(1).strip()):
                    title = bold_match.group(1).strip()
                    current_category = {"title": title, "lines": []}
                    sections["categories"].append(current_category)
                    current_section = "category"
                    continue

        if current_section == "files":
            sections["files"].append(stripped)
            continue
        if current_section == "dod":
            sections["dod"].append(stripped)
            continue
        if current_section == "verification":
            sections["verification"].append(stripped)
            continue
        if current_section == "risks":
            sections["risks"].append(stripped)
            continue

        if current_category is not None:
            current_category["lines"].append(stripped)
        else:
            sections["misc"].append(stripped)

    # Remove empty categories
    sections["categories"] = [c for c in sections["categories"] if c["lines"]]
    return sections


def _format_bullets(lines: List[str]) -> List[str]:
    formatted: List[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-"):
            formatted.append(stripped)
        else:
            formatted.append(f"- {stripped}")
    return formatted


def build_simple_issue_body(week_num: str, raw_lines: List[str]) -> str:
    body_lines = [f"# Week {week_num} Tasks", ""]
    for raw in raw_lines:
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("####"):
            body_lines.append("")
            body_lines.append(f"**{stripped.replace('#', '').strip()}**")
            continue
        body_lines.append(stripped)
    return "\n".join(body_lines).strip() + "\n"


def build_detailed_issue_body(
    phase_title: str,
    week_title: str,
    week_num: str,
    raw_lines: List[str],
    source_file: str,
    reference_docs: List[str],
) -> str:
    sections = _parse_week_sections(raw_lines)
    references = sorted(set([source_file] + reference_docs + _extract_doc_refs(raw_lines)))
    command_lines = _extract_command_lines(raw_lines)

    lines: List[str] = []

    lines.append("## 목적")
    lines.append(f"`{week_title}` 범위를 구현하여 `{phase_title}` 목표 달성에 기여한다.")
    lines.append("")

    lines.append("## 왜 필요한가")
    lines.append("- 이 이슈는 다른 작업자가 추가 맥락 없이도 바로 착수할 수 있도록 작성되었다.")
    lines.append("- 주차 단위 작업 완료 후 다음 주차 작업이 이어질 수 있어야 한다.")
    lines.append("")

    lines.append("## 참고 문서")
    if references:
        for ref in references:
            lines.append(f"- `{ref}`")
    else:
        lines.append("- [ ] 참조 문서를 추가한다.")
    lines.append("")

    lines.append("## 범위 (In Scope)")
    if sections["categories"]:
        for category in sections["categories"]:
            lines.append(f"- {category['title']}")
    else:
        lines.append(f"- {week_title}")
    lines.append("")

    lines.append("## 비범위 (Out of Scope)")
    lines.append("- 이번 주차 범위를 넘어서는 신규 기능 확장")
    lines.append("- 서버/인프라 대규모 구조 변경 (명시되지 않은 경우)")
    lines.append("")

    lines.append("## 작업 체크리스트")
    if sections["categories"]:
        for category in sections["categories"]:
            lines.append("")
            lines.append(f"### {category['title']}")
            for line in category["lines"]:
                if not line:
                    continue
                lines.append(line)
    else:
        checklist = [line.strip() for line in raw_lines if line.strip().startswith("- [")]
        if checklist:
            for item in checklist:
                lines.append(item)
        else:
            lines.append("- [ ] 주차 작업을 세부 체크리스트로 작성한다.")
    lines.append("")

    lines.append("## 구현 대상 파일 (예상)")
    file_lines = _format_bullets(sections["files"])
    if file_lines:
        lines.extend(file_lines)
    else:
        lines.append("- [ ] 변경 예상 파일을 명시한다.")
    lines.append("")

    lines.append("## Definition of Done")
    dod_lines = _format_bullets(sections["dod"])
    if dod_lines:
        lines.extend(dod_lines)
    else:
        lines.append("- [ ] 핵심 체크리스트가 모두 완료되었다.")
        lines.append("- [ ] 빌드/정적분석/테스트가 통과한다.")
        lines.append("- [ ] PR 본문에 변경 범위와 검증 결과를 남긴다.")
    lines.append("")

    lines.append("## 검증 방법")
    if sections["verification"]:
        lines.extend(sections["verification"])
    elif command_lines:
        lines.append("```bash")
        lines.extend(command_lines)
        lines.append("```")
    else:
        lines.append("```bash")
        lines.append("cd client")
        lines.append("flutter analyze")
        lines.append("flutter test")
        lines.append("```")

    lines.append("")
    lines.append("수동 검증:")
    lines.append("- [ ] 핵심 사용자 흐름 1회 이상 실행")
    lines.append("- [ ] 오류/빈 상태/로딩 상태 확인")
    lines.append("")

    lines.append("## 리스크/주의사항")
    risk_lines = _format_bullets(sections["risks"])
    if risk_lines:
        lines.extend(risk_lines)
    else:
        lines.append("- 기존 v1 경로/필드 의존 코드와 충돌 가능성을 먼저 점검한다.")
        lines.append("- 범위 외 작업은 별도 이슈로 분리한다.")
    lines.append("")

    lines.append("## Assignee Handoff")
    lines.append(f"- Week: {week_num}")
    lines.append(f"- Milestone: {phase_title}")
    lines.append("- 작업 시작 전 참고 문서와 기존 관련 PR/Issue를 확인한다.")

    return "\n".join(lines).strip() + "\n"


def parse_markdown(
    file_path: str,
    detailed_issues: bool = True,
    reference_docs: Optional[List[str]] = None,
):
    """Parses task list markdown into phase/week structures."""
    phases = []
    reference_docs = reference_docs or []

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        sys.exit(1)

    current_phase = None
    current_week = None
    current_week_raw: List[str] = []

    def finalize_current_week():
        nonlocal current_week, current_week_raw, current_phase
        if current_phase and current_week:
            if detailed_issues:
                current_week["body"] = build_detailed_issue_body(
                    phase_title=current_phase["title"],
                    week_title=current_week["title"],
                    week_num=current_week["number"],
                    raw_lines=current_week_raw,
                    source_file=file_path,
                    reference_docs=reference_docs,
                )
            else:
                current_week["body"] = build_simple_issue_body(
                    week_num=current_week["number"],
                    raw_lines=current_week_raw,
                )
            current_phase["weeks"].append(current_week)
        current_week = None
        current_week_raw = []

    for raw_line in lines:
        line = raw_line.strip()

        # Match Phase: "## 📋 Phase 1: Phase Name (Week 1-4)"
        phase_match = re.match(r"^##\s+.*?Phase\s+(\d+):\s+(.*)", line)
        if phase_match:
            finalize_current_week()
            if current_phase:
                phases.append(current_phase)

            phase_num = phase_match.group(1)
            phase_title = phase_match.group(2)
            current_phase = {
                "number": phase_num,
                "title": f"Phase {phase_num}: {phase_title}",
                "weeks": [],
            }
            continue

        # Match Week: "### Week 1: Week Goal"
        week_match = re.match(r"^###\s+Week\s+(\d+):\s+(.*)", line)
        if week_match:
            finalize_current_week()
            if current_phase:
                week_num = week_match.group(1)
                week_goal = week_match.group(2)
                current_week = {
                    "number": week_num,
                    "title": f"Week {week_num}: {week_goal}",
                    "body": "",
                }
            continue

        if current_week:
            current_week_raw.append(raw_line.rstrip("\n"))

    finalize_current_week()
    if current_phase:
        phases.append(current_phase)

    return phases


def _branch_exists(repo: str, branch_name: str) -> bool:
    cmd = ["gh", "api", f"repos/{repo}/git/ref/heads/{branch_name}", "--jq", ".ref"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def _sanitize_branch_word(word: str) -> str:
    sanitized = re.sub(r"\s+", "", word.strip().lower())
    sanitized = re.sub(r"[^a-z0-9-]", "", sanitized)
    if not sanitized:
        raise ValueError("branch word must contain at least one alphanumeric character")
    return sanitized


def _select_unique_branch_name(repo: str, phase_number: str, branch_word: str) -> str:
    """
    Branch format:
      milestone/<one-word>/phase-N

    If the candidate already exists, tries:
      milestone/<one-word>2/phase-N
      milestone/<one-word>3/phase-N
      ...
    """
    word = _sanitize_branch_word(branch_word)
    for i in range(1, 1000):
        middle = word if i == 1 else f"{word}{i}"
        candidate = f"milestone/{middle}/phase-{phase_number}"
        if not _branch_exists(repo, candidate):
            if i > 1:
                print(f"  > Branch exists, using alternative name: {candidate}")
            return candidate
    raise RuntimeError("Unable to find an available milestone branch name.")


def _open_pr_exists(repo: str, branch_name: str) -> bool:
    cmd = [
        "gh",
        "pr",
        "list",
        "--repo",
        repo,
        "--state",
        "open",
        "--head",
        branch_name,
        "--json",
        "url",
        "--jq",
        ".[0].url",
    ]
    result = run_gh_command(cmd)
    return bool(result)


def sync_to_github(phases, repo: str, branch_word: str):
    """Creates Milestones and Issues in GitHub."""
    print(f"Syncing to repository: {repo}...")

    for phase in phases:
        # Create Milestone
        print(f"Creating Milestone: {phase['title']}")
        milestone_cmd = [
            "gh",
            "api",
            f"repos/{repo}/milestones",
            "-f",
            f"title={phase['title']}",
            "--jq",
            ".number",
        ]
        milestone_number = run_gh_command(milestone_cmd)

        if not milestone_number:
            print(f"Skipping issues for {phase['title']} due to milestone error.")
            continue

        print(f"  > Created Milestone #{milestone_number}")

        # Create Issues for each week in this phase
        for week in phase["weeks"]:
            print(f"  Creating Issue: {week['title']}")
            issue_cmd = [
                "gh",
                "issue",
                "create",
                "--repo",
                repo,
                "--title",
                week["title"],
                "--body",
                week["body"],
                "--milestone",
                phase["title"],
                "--label",
                "enhancement",
            ]

            issue_url = run_gh_command(issue_cmd)
            if issue_url:
                print(f"    > Created Issue: {issue_url}")

            # Rate limiting pause
            time.sleep(1)

        # Create Milestone Branch (Integration Branch)
        # Format: milestone/<one-word>/phase-N
        branch_name = _select_unique_branch_name(repo, phase["number"], branch_word)
        print(f"Creating Integration Branch: {branch_name} from main...")

        # Get main branch SHA
        main_sha = run_gh_command([
            "gh",
            "api",
            f"repos/{repo}/git/ref/heads/main",
            "--jq",
            ".object.sha",
        ])

        if main_sha:
            tree_sha = run_gh_command([
                "gh",
                "api",
                f"repos/{repo}/git/commits/{main_sha}",
                "--jq",
                ".tree.sha",
            ])

            if tree_sha:
                empty_commit_msg = (
                    f"chore: start milestone {branch_word} phase-{phase['number']}"
                )
                new_commit_sha = run_gh_command([
                    "gh",
                    "api",
                    f"repos/{repo}/git/commits",
                    "-f",
                    f"message={empty_commit_msg}",
                    "-f",
                    f"tree={tree_sha}",
                    "-f",
                    f"parents[]={main_sha}",
                    "--jq",
                    ".sha",
                ])

                if new_commit_sha:
                    created_ref = run_gh_command([
                        "gh",
                        "api",
                        f"repos/{repo}/git/refs",
                        "-f",
                        f"ref=refs/heads/{branch_name}",
                        "-f",
                        f"sha={new_commit_sha}",
                    ])
                    if created_ref is not None:
                        print(f"  > Created Remote Branch: {branch_name} (with empty commit)")
                    else:
                        print(f"  > Failed to create remote ref for {branch_name}")
                else:
                    print("  > Failed to create empty commit. Skipping branch creation.")
            else:
                print("  > Failed to get tree SHA. Skipping branch creation.")
        else:
            print("  > Failed to get main SHA. Skipping branch creation.")

        # Create Milestone PR
        print(f"  Creating Pull Request for {branch_name}...")
        if _open_pr_exists(repo, branch_name):
            print(f"    > Open PR already exists for {branch_name}, skipping.")
        else:
            pr_title = f"[{phase['title']}] Integration PR"
            pr_body = (
                f"Integration PR for **{phase['title']}**.\\n"
                "All related feature branches for this milestone will be merged into this phase branch before a final release to `main`."
            )
            pr_url = run_gh_command([
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
                phase["title"],
            ])
            if pr_url:
                print(f"    > Created PR: {pr_url}")


def main():
    parser = argparse.ArgumentParser(description="Sync task list to GitHub Milestones and Issues.")
    parser.add_argument("--file", type=str, required=True, help="Path to the task list markdown file.")
    parser.add_argument("--repo", type=str, required=True, help="Target GitHub repository (owner/repo).")
    parser.add_argument(
        "--branch-word",
        type=str,
        default="plan",
        help="Middle one-word segment for milestone branch names. Format: milestone/<word>/phase-N",
    )
    parser.add_argument(
        "--simple-issues",
        action="store_true",
        help="Use legacy/simple issue body mode. Default is detailed assignee-ready mode.",
    )
    parser.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Reference markdown file path to include in every issue body. Can be repeated.",
    )

    args = parser.parse_args()

    phases = parse_markdown(
        file_path=args.file,
        detailed_issues=not args.simple_issues,
        reference_docs=args.reference,
    )
    if not phases:
        print("No phases found in the markdown file. Check format.")
        return

    sync_to_github(phases, args.repo, args.branch_word)


if __name__ == "__main__":
    main()
