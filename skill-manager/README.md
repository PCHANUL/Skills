# Agent Skill Manager

A package manager for AI agent skills - install, update, and manage agent skill packages.

## Installation

```bash
pip install agent-skill-manager
```

## Usage

### Install a Skill Package

```bash
# Install globally (to ~/.skills)
skill-manager install https://github.com/PCHANUL/Skills.git

# Install locally (to ./.skills in current project)
skill-manager install https://github.com/PCHANUL/Skills.git --local
```

### Update Skills

```bash
# Update all installed skills
skill-manager update

# Update a specific skill
skill-manager update Skills
```

### List Installed Skills

```bash
skill-manager list
```

### Remove a Skill

```bash
skill-manager remove Skills
```

## Storage Locations

- **Global**: `~/.skills/` (shared across all projects)
- **Local**: `./.skills/` (project-specific)

## What are Agent Skills?

Agent skills are reusable instruction sets and helper scripts for AI assistants. Each skill contains:

- `SKILL.md`: Instructions on how to perform a specific task
- `scripts/`: Helper scripts that automate parts of the workflow

## License

MIT
