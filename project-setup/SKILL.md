---
name: project-setup
description: A skill for automating GitHub milestones, week issues, and integration PR setup from a detailed project todo document, while generating assignee-ready issue bodies.
---

# Project Setup Skill

This skill bridges the gap between your planned task list and GitHub issue tracking.
It parses a Markdown plan (Phase -> Week) and syncs milestones/issues/PR scaffolding.

It is designed for handoff-ready execution: each generated week issue should be clear enough for someone unfamiliar with prior context.

## Capabilities

1. **Parse Task List**: Reads markdown with `## Phase` and `### Week` structure.
2. **Assignee-Ready Issue Bodies (Default)**: Builds detailed issue descriptions so a different contributor can execute safely.
3. **Create or Reuse Milestones**: Converts each Phase into a GitHub Milestone and reuses existing ones on reruns.
4. **Create or Update Week Issues**: Upserts issues by week title instead of duplicating.
5. **Integration Branch/PR Setup**:
- Branch format: `milestone/<one-word>/phase-N`
- If a branch already exists, auto-renames to a unique variant (for example `milestone/<one-word>2/phase-N`)

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

If source week content is sparse, the script injects actionable fallback sections.

## Prerequisites

1. Ensure `gh` CLI is authenticated (`gh auth status`).
2. Have a target repository.
3. Have a task list markdown file (for example `PROJECT_TODO.md`).
4. Prefer a planning document where each week is already written as an issue-ready section.

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

## Expected Input Format

```markdown
### Week 1: Schema Alignment & Type Contracts

**Why this week exists**
- ...

**Read first**
- ...

**Current code reality**
- ...

**Target outcome**
- ...

#### 1.1 Data Model
- [ ] ...

**Files likely touched**
- `...`

**Definition of done**
- ...

**Verification**
- `...`
```

## Sync Behavior

- Milestones are reused when the same phase title exists.
- Week issues are updated when the same week title exists.
- Integration branch names always follow `milestone/<one-word>/phase-N`.
- If the target branch name already exists, the script picks a unique branch name with a numeric suffix.
- PR creation is attempted after branch creation; when no diff exists, PR creation can be skipped by GitHub.
