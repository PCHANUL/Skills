---
name: project-task-finish
description: "Handles task completion: Commits changes -> Creates PR -> Links issues & Cleans up."
---

# Project Task Finish Skill

This skill finalizes a task and prepares it for review. Once the coding (by `code-implementer`) is done, this skill takes over to create the Pull Request and update the project tracking system.

## Capabilities

1.  **Create PR (`create_pr`)**:
    -   Automatically commits unstaged changes.
    -   Pushes the current branch to origin.
    -   **Smart PR Body**: Generates a detailed description from git commit logs.
    -   **Explicit Linking**: Adds a comment to the associated Issue linking it to the PR.
    -   (Optional) Adds "Draft" flag if more work is needed.

2.  **Test & Debug (`test_debug`)**:
    -   **(New)** Supports `--test-cmd` to run tests before finishing.
    -   **(New)** Integrates with `project-task-debugger` to autonomoulsy fix test failures.

3.  **Cleanup (`cleanup`)**:
    -   Updates the Issue status label (removes `in-progress`).
    -   Ensures correct base branch (e.g., `milestone/phase-1`).

## Usage

When implementation is complete and verified:

```bash
python3 .../finish.py --issue <issue_number> [--test-cmd "npm test"]
```
