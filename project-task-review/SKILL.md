---
name: project-task-review
description: "Reviews implementation work against the stored week-issue context: validates completion criteria, runs verification checks, and prepares review-ready context for PR feedback."
---

# Project Task Review Skill

This skill is the QA and review layer for the week-issue workflow. It should not review code in a vacuum. It must compare the implementation against:
- `Target outcome`
- `Definition of done`
- `Verification`
- remaining tasks in `TASK_PROGRESS.md`

Use this skill after implementation and before merge.

## Capabilities

1.  **Mechanical Review (`review.py`)**:
    - Reads `TASK_PROGRESS.md`.
    - Fails review when tracked tasks are incomplete.
    - Runs verification commands from the issue context or explicit CLI arguments.
    - Produces a pass/fail result that `project-driver` can consume.

2.  **Context Bundle (`qa_review.py analyze`)**:
    - Fetches changed files for a PR.
    - Loads the stored issue context and relevant full file contents.
    - Produces a structured bundle for a deeper agent review.

3.  **Post Review (`post_review`)**:
    - Uses the review result to comment, approve, or request changes on the PR.

## Instructions

### Prerequisites
- `gh` CLI authenticated.
- `git` installed.
- `TASK_PROGRESS.md` available when possible.
- `docs/CONVENTIONS.md` is optional but still useful.

### Usage

#### 1. Mechanical Review
```bash
python3 skills/project-task-review/scripts/review.py \
  --pr <pr_number> \
  --progress-file TASK_PROGRESS.md \
  --use-progress-verification \
  --json
```

This is the fast gate. It checks incomplete tasks and verification status before human or agent review.

#### 2. Deep Review Context
```bash
python3 skills/project-task-review/scripts/qa_review.py analyze \
  --pr <pr_number> \
  --progress-file TASK_PROGRESS.md
```

This produces a structured review bundle that includes issue context plus changed file contents.

#### 3. Post a Review Comment
```bash
gh pr review <pr_number> --comment --body "Review feedback..."
```

## Review Standard

The reviewer should explicitly answer:
1. Does the implementation match the `Target outcome`?
2. Are all tracked sub-tasks complete?
3. Is the `Definition of done` actually satisfied?
4. Were the required verification steps run, and did they pass?
5. Are there regressions or scope leaks outside the intended week boundary?
