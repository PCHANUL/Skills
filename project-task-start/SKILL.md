---
name: project-task-start
description: "Prepares a week-issue for implementation: reads issue context, selects the correct base branch from the milestone, creates or restores the feature branch, and marks the issue in progress."
---

# Project Task Start Skill

This skill initializes a task before implementation starts. In this repository, issues are expected to contain detailed week context, so start-up is not just about creating a branch. It should also surface the key issue context for the implementer.

## Capabilities

1.  **Start Task (`start_task`)**:
    - Fetches the issue title, body, and milestone.
    - Detects the correct integration base branch from the milestone, such as `milestone/phase-1`.
    - Creates or restores `feat/issue-{N}` from that base branch.
    - Assigns the issue to the current user and adds `in-progress`.

2.  **Surface Issue Context (`show_context`)**:
    - Extracts the week headings from the issue body:
      - `Read first`
      - `Current code reality`
      - `Target outcome`
      - `Definition of done`
      - `Verification`
    - Prints that summary so the implementer can immediately initialize `TASK_PROGRESS.md`.

3.  **Branch Safety (`branch_setup`)**:
    - Ensures the feature branch is based on the right integration branch, not an arbitrary local HEAD.
    - Reuses the branch if it already exists.
    - Leaves progress tracking to `project-task-implementer`.

## Usage

```bash
python3 skills/project-task-start/scripts/start.py --issue <issue_number>
```

## Expected Workflow

1. Read the issue and milestone.
2. Switch to the integration branch for that phase and update it.
3. Create or restore `feat/issue-{N}` from that base.
4. Mark the issue `in-progress`.
5. Print the issue context summary so the implementer can start with the correct docs and completion criteria.
