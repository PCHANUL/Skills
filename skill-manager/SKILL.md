---
name: skill-manager
description: A meta-skill for managing, indexing, and discovering other Antigravity skills.
---

# Skill Manager

This skill is designed to help you organize and discover the skills available in your environment. As the number of skills grows, it becomes crucial to have an automated way to track them.

## Capabilities

1.  **Index Skills**: Scan the `~/Skills` directory and generate a summary of all available skills.
2.  **Health Check**: (Future) Verify that all skills follow the correct format and have valid `SKILL.md` files.

## Instructions

### Setup

Before using this skill, ensure you have the necessary dependencies installed:

```bash
bash ~/Skills/skill-manager/scripts/setup_env.sh
```

### How to Index Skills

To generate an up-to-date index of all skills, run the following command:

```bash
python3 ~/Skills/skill-manager/scripts/index_skills.py
```

This will output a list of skills with their descriptions to the console. You can also redirect this output to a file if needed.

## Scripts

- `scripts/index_skills.py`: Scans directories for `SKILL.md` files, parses their YAML frontmatter, and reports the findings.
- `scripts/setup_env.sh`: Installs required Python dependencies (PyYAML).
