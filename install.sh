#!/bin/bash
set -euo pipefail

# ============================================================
# Antigravity Skills - Install Script for Claude Code
# ============================================================
# Clones the Skills repo and configures Claude Code to use them.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/PCHANUL/Skills/main/install.sh | bash
#   # or
#   git clone https://github.com/PCHANUL/Skills.git && bash Skills/install.sh
# ============================================================

REPO_URL="https://github.com/PCHANUL/Skills.git"
SKILLS_DIR="$HOME/Skills"
CLAUDE_DIR="$HOME/.claude"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"

# ---- Helpers ----

info()  { echo "[INFO]  $*"; }
warn()  { echo "[WARN]  $*"; }
error() { echo "[ERROR] $*" >&2; exit 1; }

check_dependency() {
  command -v "$1" &>/dev/null || error "'$1' is required but not installed."
}

# ---- Pre-flight checks ----

check_dependency git
check_dependency python3

# ---- 1. Clone or update the Skills repo ----

if [ -d "$SKILLS_DIR/.git" ]; then
  info "Skills repo already exists at $SKILLS_DIR. Pulling latest..."
  git -C "$SKILLS_DIR" pull origin main 2>/dev/null \
    || git -C "$SKILLS_DIR" pull origin master 2>/dev/null \
    || warn "Could not pull latest changes. Using existing version."
else
  if [ -d "$SKILLS_DIR" ]; then
    warn "$SKILLS_DIR exists but is not a git repo. Backing up to ${SKILLS_DIR}.bak"
    mv "$SKILLS_DIR" "${SKILLS_DIR}.bak.$(date +%s)"
  fi
  info "Cloning Skills repo to $SKILLS_DIR..."
  git clone "$REPO_URL" "$SKILLS_DIR"
fi

# ---- 2. Make scripts executable ----

info "Making scripts executable..."
find "$SKILLS_DIR" -name "*.sh" -exec chmod +x {} \;
find "$SKILLS_DIR" -name "*.py" -exec chmod +x {} \;

# ---- 3. Generate skill index ----

info "Generating skill index..."
if [ -f "$SKILLS_DIR/skill-manager/scripts/index_skills.py" ]; then
  python3 "$SKILLS_DIR/skill-manager/scripts/index_skills.py" "$SKILLS_DIR" 2>/dev/null || warn "Failed to generate index. Skipping."
fi

# ---- 4. Configure Claude Code (CLAUDE.md) ----

info "Configuring Claude Code..."
mkdir -p "$CLAUDE_DIR"

SKILL_BLOCK_START="<!-- SKILLS:START -->"
SKILL_BLOCK_END="<!-- SKILLS:END -->"

generate_skill_block() {
cat <<'BLOCK'
<!-- SKILLS:START -->
## Antigravity Skills

The following skills are installed at `~/Skills/`. Read the relevant `SKILL.md` before using each skill.

### Skill Index
- **project-workflow** - MASTER GUIDE: End-to-end workflow for AI software projects. Read `~/Skills/project-workflow/SKILL.md`
- **project-planner** - Phase-based project task list generation. Read `~/Skills/project-planner/SKILL.md`
- **project-setup** - GitHub Milestones & Issues sync. Read `~/Skills/project-setup/SKILL.md`
- **project-driver** - Project execution orchestrator. Read `~/Skills/project-driver/SKILL.md`
- **project-task-start** - Task initialization & branch creation. Read `~/Skills/project-task-start/SKILL.md`
- **project-task-implementer** - Core code implementation agent. Read `~/Skills/project-task-implementer/SKILL.md`
- **project-task-finish** - Task completion & PR creation. Read `~/Skills/project-task-finish/SKILL.md`
- **project-task-review** - Automated code review. Read `~/Skills/project-task-review/SKILL.md`
- **project-task-debugger** - Self-healing error fixes. Read `~/Skills/project-task-debugger/SKILL.md`
- **senior-architect** - Software architecture design. Read `~/Skills/senior-architect/SKILL.md`
- **frontend-design** - Production-grade frontend UI. Read `~/Skills/frontend-design/SKILL.md`
- **ui-ux-pro-max** - UI/UX design intelligence. Read `~/Skills/ui-ux-pro-max/SKILL.md`
- **github** - GitHub project management via gh CLI. Read `~/Skills/github/SKILL.md`
- **web_researcher** - Deep web research & reports. Read `~/Skills/web_researcher/SKILL.md`
- **skill-manager** - Package manager for skills. Read `~/Skills/skill-manager/SKILL.md`

### How to Use
When a task matches a skill above, read its `SKILL.md` first, then follow the documented workflow and scripts.
For the full project workflow, start with `~/Skills/project-workflow/SKILL.md`.
<!-- SKILLS:END -->
BLOCK
}

if [ -f "$CLAUDE_MD" ]; then
  if grep -q "$SKILL_BLOCK_START" "$CLAUDE_MD"; then
    info "Updating existing skill block in $CLAUDE_MD..."
    # Remove old block and append new one
    temp_file=$(mktemp)
    awk "/$SKILL_BLOCK_START/{skip=1} /$SKILL_BLOCK_END/{skip=0; next} !skip" "$CLAUDE_MD" > "$temp_file"
    mv "$temp_file" "$CLAUDE_MD"
    echo "" >> "$CLAUDE_MD"
    generate_skill_block >> "$CLAUDE_MD"
  else
    info "Appending skill block to existing $CLAUDE_MD..."
    echo "" >> "$CLAUDE_MD"
    generate_skill_block >> "$CLAUDE_MD"
  fi
else
  info "Creating $CLAUDE_MD..."
  generate_skill_block > "$CLAUDE_MD"
fi

# ---- Done ----

echo ""
echo "============================================"
echo "  Antigravity Skills installed successfully"
echo "============================================"
echo ""
echo "  Skills directory : $SKILLS_DIR"
echo "  Claude config    : $CLAUDE_MD"
echo ""
echo "  Claude Code will now recognize the skills"
echo "  listed in $CLAUDE_MD."
echo ""
echo "  To update skills later:"
echo "    bash ~/Skills/install.sh"
echo ""
echo "============================================"
