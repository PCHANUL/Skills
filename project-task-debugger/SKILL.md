---
name: project-task-debugger
description: "Failure-analysis agent for implementation work: reads the failing command together with `TASK_PROGRESS.md`, summarizes the gap against the issue criteria, and supports iterative retry loops."
---

# Project Task Debugger Skill

This skill handles verification or runtime failures during implementation and finishing. It is designed to work with the detailed week-issue workflow where `TASK_PROGRESS.md` already contains:
- `Current code reality`
- `Target outcome`
- `Files likely touched`
- `Definition of done`
- `Verification`

The debugger should use that stored context when deciding what to inspect and what to fix next.

## Capabilities

1.  **Analyze Failure (`analyze_error`)**:
    - Reads the failed command output.
    - Reads `TASK_PROGRESS.md` to recover the issue title, current code reality, target outcome, and remaining tasks.
    - Writes a focused debug report so the agent can resume without re-reading the entire issue.

2.  **Propose Fix (`propose_fix`)**:
    - Chooses the smallest fix that addresses the failure and still respects the issue's `Definition of done`.
    - Uses `Files likely touched` and `Current code reality` to avoid random edits outside the intended scope.

3.  **Apply & Verify (`apply_fix`)**:
    - Reruns the failed command after a fix.
    - Supports interactive retry loops for manual debugging.
    - Supports non-interactive failure analysis for automated callers such as `project-task-finish`.

## Usage

### Interactive Manual Debugging
```bash
python3 skills/project-task-debugger/scripts/debug.py \
  --command "./scripts/client_build_web.sh" \
  --progress-file TASK_PROGRESS.md \
  --interactive
```

### Non-Interactive Failure Report
```bash
python3 skills/project-task-debugger/scripts/debug.py \
  --command "flutter analyze" \
  --progress-file TASK_PROGRESS.md
```

This writes `TASK_DEBUG.md` with:
- failing command
- failure excerpt
- current issue context
- remaining tasks
- likely files to inspect

### Integrated Workflow (Local)
`project-task-finish` or `project-driver` can call this to generate a failure report before handing control back for fixes.

### Integrated Workflow (CI/CD)
To enable true autonomous self-healing in your CI pipeline, you can use the `github-actions-template/workflows/ci-auto-fix.yml` template.
When tests fail on a Pull Request, this workflow will automatically post a comment such as `/agent The CI tests failed...`, which wakes up the `github-cloud-agent` to analyze the CI logs and push a fix.

## Debugging Strategy

1. Isolate the failure command or the smallest failing check.
2. Read the stored task context before editing.
3. Compare the failure against `Current code reality` and `Target outcome`.
4. Apply the smallest fix that preserves the task boundary.
5. Rerun the command and update the debug report if the failure changes.
