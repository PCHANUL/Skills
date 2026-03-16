---
name: project-driver
description: "The orchestrator for the week-issue workflow: reads detailed issue context, coordinates implementer/debugger/review/finish, and advances milestone work issue by issue."
---

# Project Driver Skill

This skill is the project orchestrator. It does not replace the implementation agent. It coordinates the full cycle around the detailed week-issue format and keeps the process aligned with the stored task context.

## Capabilities

1.  **Iterate Milestone (`drive_milestone`)**:
    - Fetches open issues for a milestone.
    - Processes them in order.
    - Restores interrupted state when needed.

2.  **Execute Cycle (`execute_cycle`)**:
    - Calls `project-task-start`.
    - Extracts the key week context from the GitHub issue body.
    - Hands off to `project-task-implementer` with explicit notes about `Read first`, `Target outcome`, and `Verification`.
    - Calls `project-task-finish` with progress-aware verification.
    - Calls `project-task-review` as the objective gate.
    - Loops back through implementation and debugging when review fails.

3.  **Release Milestone (`create_release`)**:
    - Creates the release PR from the milestone integration branch to `main`.
    - Summarizes closed milestone issues in the release body.

## Instructions

### Usage

To drive a milestone:

```bash
python3 skills/project-driver/scripts/drive.py --milestone "Phase 1: v2 Data Model & Contracts"
```

The driver is still interactive at the implementation boundary, but it should automate the context and review handoff around that pause.

### Workflow
1. Driver fetches the next issue and prints the week context summary.
2. Driver runs `project-task-start`.
3. Agent uses `project-task-implementer` and stores context in `TASK_PROGRESS.md`.
4. Driver runs `project-task-finish --use-progress-verification`.
5. Driver runs `project-task-review` against the resulting PR.
6. If review fails, driver points the agent to `project-task-debugger` or another implementation pass.
7. If review passes, driver merges, closes the issue, and updates the integration PR.
