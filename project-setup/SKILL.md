---
name: project-setup
description: A skill for automating GitHub Milestones and Issues creation based on a structured task list (from task-manager).
---

# Project Setup Skill

This skill bridges the gap between your planned task list and GitHub issue tracking.
It parses a Markdown plan (Phase -> Week) and creates GitHub milestones/issues.

## Capabilities

1. **Parse Task List**: Reads markdown with `## Phase` and `### Week` structure.
2. **Create Milestones**: Converts each Phase into a GitHub Milestone.
3. **Create Issues**: Converts each Week into a GitHub Issue linked to the matching milestone.
4. **Assignee-Ready Issue Bodies (Default)**: Builds detailed issue descriptions so someone unfamiliar with the codebase can execute safely.
5. **Milestone Branch/PR Setup**: Creates milestone integration branches and PRs when applicable.
   - Branch format: `milestone/<one-word>/phase-N`
   - If branch already exists, auto-renames to a unique variant (e.g., `milestone/<one-word>2/phase-N`)

## Issue Quality Standard (Required)

Every generated issue should be usable by a different contributor without extra verbal context.
The issue body must include:

- `목적 / Goal`
- `왜 필요한가 / Background`
- `참고 문서 / References`
- `범위 (In Scope)`
- `비범위 (Out of Scope)`
- `작업 체크리스트 (카테고리별)`
- `구현 대상 파일 (가능하면)`
- `Definition of Done`
- `검증 방법 (commands + manual checks)`
- `리스크/주의사항`

If a source week section is missing, the script injects actionable fallback content rather than leaving the issue sparse.

## Prerequisites

1. Ensure `gh` CLI is authenticated (`gh auth status`).
2. Have a target repository.
3. Have a task list markdown file (for example `PROJECT_TODO.md`).

## Usage

### Recommended (detailed issue bodies)

```bash
python3 ~/Skills/project-setup/scripts/sync_to_github.py \
  --file "PROJECT_TODO.md" \
  --repo "username/repo-name" \
  --branch-word "interface" \
  --reference "docs/v2/08_INTERFACE_PLANNING.md" \
  --reference "docs/v2/09_INTERFACE_TASK_LIST.md"
```

### Legacy/simple issue bodies

```bash
python3 ~/Skills/project-setup/scripts/sync_to_github.py \
  --file "PROJECT_TODO.md" \
  --repo "username/repo-name" \
  --branch-word "interface" \
  --simple-issues
```

## Notes

- Prefer the detailed mode unless explicitly asked otherwise.
- When the same milestone branch name already exists, the script must choose a new branch name using the same format.
- Keep generated issue language aligned with the task list language (Korean docs -> Korean issue bodies).
