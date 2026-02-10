---
name: skill-manager
description: "A package manager and index generator for AI agent skills."
---

# Skill Manager

This skill manages the installation, updating, and indexing of AI agent skills. Think of it as `npm` or `pip` for agent skills.

## Capabilities

1.  **Install Skills (`install`)**: Download and install skill packages from GitHub.
2.  **Update Skills (`update`)**: Pull latest changes for installed skills.
3.  **List Skills (`list`)**: Show all installed skills (global and local).
4.  **Remove Skills (`remove`)**: Uninstall a skill.
5.  **Index Skills**: Generate an index of available skills.

## Usage

### Install a Skill
```bash
# Install globally (to ~/.skills)
python3 ~/Skills/skill-manager/scripts/skill_manager.py install https://github.com/PCHANUL/Skills.git

# Install locally (to ./.skills in current project)
python3 ~/Skills/skill-manager/scripts/skill_manager.py install https://github.com/PCHANUL/Skills.git --local
```

### Update Skills
```bash
# Update all installed skills
python3 ~/Skills/skill-manager/scripts/skill_manager.py update

# Update a specific skill
python3 ~/Skills/skill-manager/scripts/skill_manager.py update Skills
```

### List Installed Skills
```bash
python3 ~/Skills/skill-manager/scripts/skill_manager.py list
```

### Remove a Skill
```bash
python3 ~/Skills/skill-manager/scripts/skill_manager.py remove Skills
```

### Index Skills (Legacy)
```bash
python3 ~/Skills/skill-manager/scripts/index_skills.py ~/Skills
```

## Storage Locations

-   **Global**: `~/.skills/` (shared across all projects)
-   **Local**: `./.skills/` (project-specific, add to `.gitignore` if needed)

## Scripts

-   `scripts/skill_manager.py`: Main CLI for install/update/list/remove.
-   `scripts/index_skills.py`: Generates skill index from SKILL.md files.
-   `scripts/setup_env.sh`: Installs required Python dependencies (PyYAML).
