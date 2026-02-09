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
    -   Creates a Pull Request with a proper title and description (`Closes #123`).
    -   (Optional) Adds "Draft" flag if more work is needed.

2.  **Link & Cleanup (`link_cleanup`)**:
    -   Links the generated PR to the Issue as a comment.
    -   Updates the Issue status label (removes `in-progress`).
    -   (Optional) Moves project cards or adds reviewers.

## Usage

When implementation is complete and verified:

```bash
python3 ~/Skills/project-task-finish/scripts/finish.py --issue <issue_number>
```
