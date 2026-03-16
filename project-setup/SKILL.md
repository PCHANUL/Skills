---
name: project-setup
description: A skill for automating GitHub milestones, week issues, and integration PR setup from a detailed project todo document, especially when each week section is issue-ready and self-contained.
---

# Project Setup Skill

This skill bridges the gap between your planned task list and GitHub's issue tracking system. It reads a Markdown file, parses the phases and weeks, and automatically sets up your GitHub repository.

It should preserve issue-ready weekly detail. If the planning document includes week sections with implementation context such as `Why this week exists`, `Read first`, `Current code reality`, `Target outcome`, `Files likely touched`, `Definition of done`, and `Verification`, those sections should be copied into the GitHub issue body without flattening them into a minimal checklist.

## Capabilities

1.  **Parse Task List**: Reads a markdown file structured with `## Phase` and `### Week` headers.
2.  **Preserve Rich Week Context**: Copies detailed week sections into issues with minimal transformation.
3.  **Create or Reuse Milestones**: Converts each `Phase` into a GitHub Milestone and reuses it on reruns.
4.  **Create or Update Issues**: Converts each `Week` into a GitHub Issue, linked to the corresponding Milestone, and updates existing matching issues instead of duplicating them.
5.  **Create or Reuse Integration Branch/PR**: Sets up milestone branches and PRs while avoiding duplicate creation on reruns.

## Instructions

### Prerequisites
1.  Ensure `gh` CLI is authenticated (`gh auth status`).
2.  Have a target repository ready.
3.  Have a task list markdown file (e.g., `PROJECT_TODO.md`).
4.  Prefer a planning document where each week is already written as an issue-ready section.

### Usage
Run the python script with the path to your task list and the target repository.

```bash
python3 ~/Skills/project-setup/scripts/sync_to_github.py --file "PROJECT_TODO.md" --repo "username/repo-name"
```

### Expected Input Format
The best input format is a project todo document where every week is independently actionable, for example:

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

### Sync Behavior
- Milestones should be reused if the same phase title already exists.
- Week issues should be updated if the same week title already exists.
- Integration branches and milestone PRs should be reused if they already exist.
- The script should keep week markdown readable in GitHub issues instead of flattening it into a lossy summary.
