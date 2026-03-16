---
name: project-planner
description: A skill for generating highly detailed, issue-ready phase-based project task lists in Markdown format, especially when each week may be implemented by a different person.
---

# Project Planner Skill

This skill is designed to break down complex projects into actionable, granular tasks. It promotes a structured approach using Phases, Weeks, and specific Task Items, ensuring comprehensive project planning and tracking.

The default output should be suitable for direct conversion into GitHub week issues. Assume the person implementing a given week may not know prior context. Each week section must therefore contain enough context to execute independently.

## Capabilities

1.  **Generate Project Blueprint**: Create a detailed Markdown file with a standardized structure (Phase -> Week -> Context -> Work Items -> Verification).
2.  **Generate Issue-Ready Week Sections**: Ensure each week contains enough context to be pasted directly into a GitHub issue body.
3.  **Standardize Planning**: Enforce a consistent format for project roadmaps, making them easier to read and manage.

## Instructions

### Intelligent Planning Automation (Recommended)
You can now use AI to generate project plan options based on your idea, and automatically create a detailed task list based on your choice.

**Prerequisite:** Ensure `LLM_API_KEY` is exported in your environment.

```bash
python3 ~/Skills/project-planner/scripts/plan_generator.py
```
Or provide an idea directly:
```bash
python3 ~/Skills/project-planner/scripts/plan_generator.py --idea "Build a habit tracking iOS app"
```

The script will:
1. Propose 3 distinct structural approaches based on your idea.
2. Ask you to choose the preferred approach.
3. Generate a highly detailed `PROJECT_TODO.md` file automatically.
4. Structure each week so a different implementer can execute it without prior conversation context.

### Manual Template Generation
If you prefer to manually fill in the task list, you can generate a blank template. You can customize the number of phases and weeks.

```bash
python3 ~/Skills/project-planner/scripts/generate_task_list.py --output "PROJECT_TODO.md" --title "My Project" --phases 3 --weeks 4
```

### Template Structure
The generated file (whether AI or manual) will follow this structure:

```markdown
# [Project Name] Detailed Todo List
> [Description]

## 📋 Phase 1: [Phase Name] (Week 1-4)
### Week 1: [Week Goal]
**Why this week exists**
- [Short explanation of why this work matters now]

**Read first**
- [Spec / design / architecture docs to read before coding]

**Current code reality**
- [What is true in the current implementation]

**Target outcome**
- [What must be true when the week is done]

#### 1.1 [Category]
- [ ] [Specific Task]
- [ ] [Specific Task]

**Files likely touched**
- `[path/to/file]`

**Definition of done**
- [Observable completion criteria]

**Verification**
- `[command]`
```

### Best Practices for Filling the List
1.  **Write for handoff**: Assume the assignee for Week N has not read Week N-1. Include enough context to execute safely.
2.  **Be Specific**: Instead of "implement auth", write "Create login UI", "Connect Firebase Auth", "Handle error states".
3.  **Include current-state diagnosis**: Each week should state what is wrong or incomplete in the current code.
4.  **Include references**: Point to exact specs, docs, or architecture files that must be read first.
5.  **Define completion concretely**: Add a short Definition of Done and Verification section for every week.
6.  **Review Intervals**: Plan for testing and validation, not just coding.

### Required Week-Level Sections
Every generated week section should contain all of the following unless clearly inapplicable:

1.  `Why this week exists`
2.  `Read first`
3.  `Current code reality`
4.  `Target outcome`
5.  `Work categories` with actionable checklist items
6.  `Files likely touched`
7.  `Definition of done`
8.  `Verification`

### When Planning Refactors or Migrations
If the project involves replacing an existing system, every relevant week should explicitly state:

1.  What legacy shape or path currently exists
2.  What the target shape or path will become
3.  Whether the week is allowed to leave compatibility shims in place
4.  What must be verified to confirm the migration boundary is safe
