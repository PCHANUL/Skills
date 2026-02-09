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

### Usage
To generate a new detailed task list, use the provided Python script. You can customize the number of phases and weeks.

```bash
python3 ~/Skills/project-planner/scripts/generate_task_list.py --output "PROJECT_TODO.md" --title "My Project" --phases 3 --weeks 4
```

### Template Structure
The generated file will follow this structure:

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
