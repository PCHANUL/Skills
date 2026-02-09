---
name: project-task-implementer
description: "The core implementation agent: Analyzes requirements -> Breaks down into sub-tasks -> Implements iteratively -> Verifies code."
---

# Project Task Implementer Skill

This skill is the "brain" of the development process. It focuses purely on analyzing requirements and writing the actual code to fulfill the task. 

**CRITICAL PRINCIPLE**: Do NOT implement everything at once. Break down the task into small, manageable sub-tasks and implement them iteratively.

## Capabilities

1.  **Analyze & Breakdown (`analyze_req`)**:
    -   Reads the GitHub Issue or requirement document.
    -   **Action**: Breaks down the issue into a checklist of **Sub-Tasks** (e.g., [ ] Domain Model, [ ] Repository, [ ] UI Layout).
    -   **Action**: Identifies necessary file changes or creations.

2.  **Iterative Implementation (`implement_subtask`)**:
    -   **Focus**: Pick ONE sub-task from the breakdown list.
    -   **Design**: Apply architectural patterns (e.g., Clean Architecture) for this specific sub-task.
    -   **Code**: Write the code layer by layer.
    -   **Verify**: Run syntax checks (`dart analyze`, etc.) immediately after writing.

3.  **Check Progress (`status_check`)**:
    -   Review what has been implemented so far.
    -   Decide if the feature is complete enough to move to `project-task-finish` or if more sub-tasks remain.

## Usage (Agent Workflow)

When `project-driver` hands over control:

1.  **Analyze & Initialize**:
    -   Read the issue. (e.g., "Implement Login")
    -   **Run `track_progress.py init`**: Break down the task into sub-tasks immediately.
        ```bash
        python3 ~/Skills/project-task-implementer/scripts/track_progress.py init "Create Auth Entity" "Implement Auth Repo" "Create Login Bloc" "Build UI"
        ```

2.  **Execute Sub-Task 1**:
    -   **Run `track_progress.py list`**: See what needs to be done.
    -   "Starting Task 1: Create Auth Entity..." -> Write code.
    -   **Run `track_progress.py complete 1`**: Mark as done. The script will tell you the next task.

3.  **Context Recovery (If needed)**:
    -   If interrupted, simply run `python3 .../track_progress.py list` to restore context.

4.  **Completion**:
    -   When all tasks are marked `[x]`, verify functionality.
    -   Return control to driver.
