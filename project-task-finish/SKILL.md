---
name: project-task-finish
description: "Finalizes an implementation task using the stored issue context: checks completion against explicit done criteria, runs verification, creates or updates the PR, and records the handoff."
---

# Project Task Finish Skill

This skill finalizes a task and prepares it for review. It assumes implementation work was tracked in `TASK_PROGRESS.md` and uses that context to produce a review-ready handoff.

For this repository, week issues are expected to include:
- `Why this week exists`
- `Read first`
- `Current code reality`
- `Target outcome`
- `Definition of done`
- `Verification`

The finish step must not treat "all files changed" as equivalent to "task complete". It should verify the work against the stored issue criteria.

## Capabilities

1.  **Create PR (`create_pr`)**:
    - Automatically stages and commits changes.
    - Pushes the current branch to origin.
    - Builds a PR body from:
      - issue title
      - source of truth
      - target outcome
      - completed tasks
      - verification results
      - commit summary
    - Creates a new PR or updates the existing PR for the current branch.
    - Adds an issue comment with the PR link and completion summary.

2.  **Completion Gate (`completion_gate`)**:
    - Reads `TASK_PROGRESS.md` before finishing.
    - Checks whether any tracked tasks are still incomplete.
    - Uses `Definition of done` and `Verification` to drive the final validation.
    - Refuses to create a normal PR if tasks remain incomplete unless explicitly allowed.

3.  **Verification (`test_debug`)**:
    - Supports explicit verification commands through `--verification-cmd`.
    - Supports test execution through `--test-cmd`.
    - If needed, can delegate failed verification to `project-task-debugger`.
    - Records which verification commands passed, failed, or were not run.

4.  **Cleanup (`cleanup`)**:
    - Removes `in-progress` from the issue when possible.
    - Uses the milestone to determine the correct integration base branch, such as `milestone/phase-1`.
    - Supports draft PR creation when verification or scope is incomplete.

## Usage

When implementation is complete or ready for review:

```bash
python3 skills/project-task-finish/scripts/finish.py \
  --issue <issue_number> \
  [--use-progress-verification] \
  [--test-cmd "./scripts/client_build_web.sh"] \
  [--verification-cmd "flutter analyze"] \
  [--verification-cmd "npm test"] \
  [--dry-run] \
  [--draft]
```

## Expected Workflow

1. Read `TASK_PROGRESS.md`.
2. Confirm the tracked tasks are complete.
3. Review `Definition of done` and `Verification`.
4. Run the relevant verification commands.
5. Commit and push the branch.
6. Create or update the PR with a body derived from the stored issue context.
7. Comment on the issue with:
   - PR link
   - verification status
   - any remaining gaps or deferred work

If `TASK_PROGRESS.md` is missing, the skill may still proceed, but it should say that the finish context is incomplete and fall back to issue metadata plus git history.
