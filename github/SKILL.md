---
name: github
description: A skill for managing GitHub projects, issues, and pull requests using the gh CLI.
---

# GitHub Skill

This skill allows you to interact with GitHub directly from your terminal using the `gh` CLI. It provides capabilities for project management, issue tracking, and pull request handling.

## specific_capabilities

1.  **Issue Management**: Create, list, edit, and view GitHub issues.
2.  **Pull Request Management**: Create, list, checkout, and review pull requests.
3.  **Project Management**: Interact with GitHub Projects (beta) to manage items and views.
4.  **Repo Management**: Clone, create, and list repositories.

## Instructions

### Prerequisites
Ensure the `gh` CLI is authenticated:
```bash
gh auth status
```
If not authenticated, run `gh auth login`.

### Common Commands

#### Issues
- **List issues**: `gh issue list`
- **Create issue**: `gh issue create --title "Title" --body "Description"`
- **View issue**: `gh issue view <number>`
- **Comment on issue**: `gh issue comment <number> --body "Comment"`

#### Pull Requests
- **List PRs**: `gh pr list`
- **Checkout PR**: `gh pr checkout <number>`
- **Create PR**: `gh pr create`
- **Merge PR**: `gh pr merge <number>`

#### Projects
- **List projects**: `gh project list`
- **View project**: `gh project view <number>`

## Examples

### Check specific issue details
```bash
gh issue view 123
```

### Create a bug report
```bash
gh issue create --label "bug" --title "App crashes on launch" --body "Steps to reproduce..."
```
