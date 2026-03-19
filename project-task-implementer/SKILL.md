---
name: project-task-implementer
description: "The core implementation agent: reads an issue-ready week spec, extracts execution context, breaks work into sub-tasks, implements iteratively, and verifies against explicit done criteria."
---

# Project Task Implementer Skill

This skill is the implementation engine. It turns a GitHub issue or planning document into a concrete execution loop with explicit context tracking.

**CRITICAL PRINCIPLE**: Do NOT implement everything at once. Break the task into small, coherent sub-tasks and implement them iteratively.

For this repository, week issues are expected to be detailed and usually contain sections such as:
- `Why this week exists`
- `Read first`
- `Current code reality`
- `Target outcome`
- `Files likely touched`
- `Out of scope`
- `Definition of done`
- `Verification`

The implementer must preserve that context before coding so another agent can recover the task state without re-reading the entire issue.

## Capabilities

1.  **Issue Context Extraction (`analyze_req`)**:
    - Reads the GitHub Issue or requirement document.
    - Extracts the execution context, not just the checklist.
    - At minimum, capture:
      - issue title
      - source of truth document
      - `Read first`
      - `Current code reality`
      - `Target outcome`
      - `Definition of done`
      - `Verification`
    - If the issue body is missing detail, check the matching section in `docs/v2/V2_PROJECT_TODO.md` and any referenced v2 docs before implementing.

2.  **Sub-Task Breakdown (`plan_subtasks`)**:
    - Break the issue into a short checklist of implementation sub-tasks.
    - Do not blindly copy every issue bullet into the tracker. Collapse them into executable units.
    - Each sub-task should have a concrete boundary, such as:
      - schema/type alignment
      - repository path rewrite
      - callable function contract update
      - UI flow update
      - verification/codegen
    - Identify files likely to change before editing.

3.  **Iterative Implementation (`implement_subtask`)**:
    - Focus on one sub-task at a time.
    - Keep the issue's `Current code reality` and `Target outcome` visible while editing.
    - Prefer finishing one contract boundary end-to-end before moving to the next.
    - After each sub-task, run the smallest useful verification and update the progress tracker.

4.  **Completion Check (`status_check`)**:
    - Review completed work against `Definition of done`, not just the original task list.
    - Run or report the issue's `Verification` steps.
    - Call out any remaining gaps explicitly before handing off to `project-task-finish`.

## Usage (Agent Workflow)

When a detailed week issue or implementation document is provided:

1.  **Read and Extract Context**:
    - Read the issue body and referenced docs.
    - Extract:
      - title
      - source doc
      - `Read first`
      - `Current code reality`
      - `Target outcome`
      - `Definition of done`
      - `Verification`
    - If the issue is derived from `docs/v2/V2_PROJECT_TODO.md`, keep the section wording close to the source.

2.  **Initialize Progress Tracking Immediately**:
    - Run `track_progress.py init` before coding.
    - Include the extracted context so task recovery does not depend on memory.
    - Example:
      ```bash
      python3 skills/project-task-implementer/scripts/track_progress.py init \
        --force \
        --title "Week 1: Schema Alignment & Type Contracts" \
        --source "docs/v2/V2_PROJECT_TODO.md" \
        --read-first "docs/v2/01_SERVICE_OVERVIEW.md sections 2, 3, 4, 7" \
        --read-first "docs/v2/02_EPISODE_AND_SCENE.md sections 1, 2, 3, 5" \
        --current-code-reality "Server story path is still centered on stories/{storyId}." \
        --current-code-reality "Choice payloads still exist in v1 format in runtime paths." \
        --target-outcome "Server and client agree on the v2 contract for CharacterCard, Episode, Scene, Choice, and state changes." \
        --definition-of-done "Server and client v2 types compile." \
        --definition-of-done "Generated Dart files are updated." \
        --verification "flutter pub run build_runner build --delete-conflicting-outputs" \
        --verification "flutter analyze" \
        "Update server story/card types" \
        "Update client episode/scene/choice/state entities" \
        "Regenerate Dart codegen and resolve compile issues"
      ```

3.  **Implement Iteratively**:
    - Run `track_progress.py context` or `track_progress.py list` to restore task state.
    - Pick one sub-task.
    - Implement only that boundary.
    - Run the smallest relevant verification step.
    - Mark the sub-task complete.

4.  **Recover Context After Interruptions**:
    - Use `python3 skills/project-task-implementer/scripts/track_progress.py context` to recover the stored issue context.
    - Use `python3 skills/project-task-implementer/scripts/track_progress.py list` to see remaining work.

5.  **Finish Against Explicit Criteria**:
    - When all sub-tasks are marked done, verify the work against `Definition of done` and `Verification`.
    - If some verification cannot be run, record that explicitly.
    - Only then hand off to `project-task-finish`.
