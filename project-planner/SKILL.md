---
name: project-planner
description: A skill for generating highly detailed, phase-based project task lists in Markdown format.
---

# Project Planner Skill

This skill is designed to break down complex projects into actionable, granular tasks. It promotes a structured approach using Phases, Weeks, and specific Task Items, ensuring comprehensive project planning and tracking.

## Capabilities

1.  **Generate Project Blueprint**: Create a detailed Markdown file with a standardized structure (Phase -> Week -> Category -> Task).
2.  **Standardize Planning**: Enforce a consistent format for project roadmaps, making them easier to read and manage.

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
#### 1.1 [Category]
- [ ] [Specific Task]
  ```bash
  [Command context if needed]
  ```
```

### Best Practices for Filling the List
1.  **Be Specific**: Instead of "implement auth", write "Create login UI", "Connect Firebase Auth", "Handle error states".
2.  **Add Context**: Use code blocks or comments to add implementation details (e.g., file paths, API endpoints).
3.  **Review Intervals**: Plan for "Refactoring" or "Testing" weeks between major phases.
