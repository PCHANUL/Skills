---
name: project-task-start
description: "Prepares the development environment: Assigns issue -> Creates branch -> Scaffolds file structure."
---

# Project Task Start Skill

This skill handles the initialization phase of a development task. It ensures that every task starts with a standardized git branch and a clean file structure ready for implementation.

## Capabilities

1.  **Start Task (`start_task`)**:
    -   Fetches issue details.
    -   Assigns the issue to the current user.
    -   Updates issue labels (adds `in-progress`).
    -   Creates and checks out a feature branch (`feat/issue-{N}`).

2.  **Scaffold Task (`scaffold_task`)**:
    -   Analyzes the issue description for required files.
    -   Creates empty files and directories to establish the project structure.
    -   (Optional) Populates files with basic boilerplate.

## Usage

```bash
python3 ~/Skills/project-task-start/scripts/start.py --issue <issue_number>
```
