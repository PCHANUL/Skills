---
name: project-driver
description: "The orchestrator that drives the project forward by iterating through open issues and executing the full development cycle (Start -> Implement -> Finish) for each one."
---

# Project Driver Skill

This skill is the **Project Manager Agent**. It doesn't write code itself, but it manages the flow of work. It looks at the GitHub Project (or Milestone), picks the next available task, and instructs the `project-task-*` skills to execute it. Then it repeats this process until all tasks in the milestone are complete.

## Capabilities

1.  **Iterate Milestone (`drive_milestone`)**:
    -   Fetches all open issues for a specific Milestone.
    -   Sorts them by priority or dependency (if labeled).
    -   Sequentially executes the development cycle for each issue.

2.  **Execute Cycle (`execute_cycle`)**:
    -   Calls `project-task-start` to initialize the task.
    -   **Pauses** to let the Agent (User) or `project-task-implementer` do the coding.
    -   Calls `project-task-finish` to create the PR.
    -   Calls `project-task-review` to check the PR.

## Instructions

### Usage

To start driving a specific milestone:

```bash
python3 ~/Skills/project-driver/scripts/drive_project.py --milestone "Phase 1: Setup"
```

**Note**: This script is designed to be interactive. It will likely ask for confirmation before starting the next task or after the implementation step is done.

### Workflow
1.  **Driver**: "Found 5 open issues in Milestone 'Phase 1'. Starting Issue #1: 'Setup Project Structure'."
2.  **Driver**: Executes `project-task-start`.
3.  **Driver**: "Task #1 waiting for implementation. Agent, please implement the code now."
4.  **Agent**: (Uses `project-task-implementer` to write code).
5.  **Driver**: "Implementation marked as done. Running `project-task-finish` to create/update PR."
6.  **Driver**: "Running `project-review` check..."
    -   If **Passed**: Automerge and proceed to next issue.
    -   If **Changes Requested**: Loop back to Step 3 (Implementation) for fixes.
