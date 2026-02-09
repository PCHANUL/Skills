---
name: project-task-review
description: "Automates the verification phase: Automated Code Review (Lint + Context-aware LLM Analysis) and PR Checks."
---

# Project Task Review Skill

This skill acts as your automated Quality Assurance engineer. It reviews Pull Requests not just for syntax errors, but for architectural compliance and logic issues by analyzing code within its full file context.

## Capabilities

1.  **Analyze PR (`analyze_pr`)**: 
    -   Fetches the Diff of a PR.
    -   Identifies changed files and retrieves their **full content** for context.
    -   Runs project-specific linters (e.g., `flutter analyze`).
    -   (Agent-Driven) Uses the context to generate a code review based on `CONVENTIONS.md`.    
2.  **Post Review (`post_review`)**:
    -   Posts the generated review comments to the PR using `gh pr review`.
    -   Can approve, request changes, or simply comment.

## Instructions

### Prerequisites
-   `gh` CLI authenticated.
-   `git` installed.
-   A `docs/CONVENTIONS.md` file in your repository (recommended for better reviews).

### Usage

#### 1. Analyze a Pull Request
This command gathers all necessary context (Diff + Full Files + Linter Output) and prepares a prompt for the Agent to perform the review.

```bash
python3 ~/Skills/project-review/scripts/qa_review.py analyze --pr <pr_number>
```

**Agent Action**: The script outputs a structured prompt. The Agent should read this, perform the review using its intelligence, and then use `post_review` (or `gh` directly) to submit feedback.

#### 2. Post a Review Comment (Shortcut)
```bash
gh pr review <pr_number> --comment --body "Review feedback..."
```
