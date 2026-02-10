---
name: project-task-debugger
description: "Self-Healing Agent: Analyzes failures, proposes fixes, and retries using iterative debugging loops."
---

# Project Task Debugger Skill

This skill is the **"Emergency Response Unit"**. When tests fail or lint errors block progress, this skill steps in to autonomously fix the issue.

## Capabilities

1.  **Analyze Failure (`analyze_error`)**:
    -   Reads `stderr` / `stdout` from failed commands.
    -   Locates the file and line number causing the error.
    -   **Action**: Summarizes the root cause (e.g., "NullPointerException at login_bloc.dart:45").

2.  **Propose Fix (`propose_fix`)**:
    -   Generates a code patch based on the analysis.
    -   **Safety**: Verifies the fix doesn't break other tests (runs full suite if possible).

3.  **Apply & Verify (`apply_fix`)**:
    -   Edits the file.
    -   Reruns the failed command.
    -   **Loop**: If still failing, retries up to **3 times**. If success, returns control to caller.

## Usage

### Manual Invocation
```bash
python3 ~/Skills/project-task-debugger/scripts/debug.py --command "npm test"
```

### Integrated Workflow
`project-task-finish` calls this automatically if tests fail.

## Debugging Strategy

1.  **Isolate**: Run only the failing test suite if possible.
2.  **Read Context**: Use `view_file` on the error location.
3.  **Reason**: "Why did this fail? Logic error? Syntax? Missing import?"
4.  **Fix**: Apply minimal change.
5.  **Regress**: Ensure no new errors introduced.
