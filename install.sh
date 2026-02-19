#!/bin/bash
set -euo pipefail

# ============================================================
# Antigravity Skills - Install & Update Script for Claude Code
# ============================================================
#
# Usage:
#   bash install.sh              # Install (clone + configure)
#   bash install.sh --update     # Update (pull + re-scan skills)
#
#   # One-liner install:
#   curl -fsSL https://raw.githubusercontent.com/PCHANUL/Skills/main/install.sh | bash
# ============================================================

REPO_URL="https://github.com/PCHANUL/Skills.git"
SKILLS_DIR="$HOME/Skills"
CLAUDE_DIR="$HOME/.claude"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"

SKILL_BLOCK_START="<!-- SKILLS:START -->"
SKILL_BLOCK_END="<!-- SKILLS:END -->"

# ---- Helpers ----

info()  { echo "[INFO]  $*"; }
warn()  { echo "[WARN]  $*"; }
error() { echo "[ERROR] $*" >&2; exit 1; }

check_dependency() {
  command -v "$1" &>/dev/null || error "'$1' is required but not installed."
}

# ---- Parse SKILL.md frontmatter ----

parse_skill() {
  local skill_md="$1"
  local name="" description=""

  while IFS= read -r line; do
    if [[ "$line" =~ ^name:\ *(.+)$ ]]; then
      name="${BASH_REMATCH[1]}"
      name="${name#\"}" ; name="${name%\"}"
    elif [[ "$line" =~ ^description:\ *(.+)$ ]]; then
      description="${BASH_REMATCH[1]}"
      description="${description#\"}" ; description="${description%\"}"
    fi
  done < <(sed -n '/^---$/,/^---$/p' "$skill_md" | grep -v '^---$')

  if [ -n "$name" ] && [ -n "$description" ]; then
    echo "$name|$description"
  fi
}

# ---- Generate skill block dynamically ----

generate_skill_block() {
  local skills_dir="$1"

  echo "$SKILL_BLOCK_START"
  echo "## Antigravity Skills"
  echo ""
  echo 'The following skills are installed at `~/Skills/`. Read the relevant `SKILL.md` before using each skill.'
  echo ""
  echo "### Skill Index"

  for skill_md in "$skills_dir"/*/SKILL.md; do
    [ -f "$skill_md" ] || continue
    local parsed
    parsed=$(parse_skill "$skill_md")
    [ -z "$parsed" ] && continue

    local name="${parsed%%|*}"
    local desc="${parsed#*|}"
    echo "- **${name}** - ${desc} Read \`~/Skills/${name}/SKILL.md\`"
  done

  echo ""
  echo "### How to Use"
  echo 'When a task matches a skill above, read its `SKILL.md` first, then follow the documented workflow and scripts.'
  echo 'For the full project workflow, start with `~/Skills/project-workflow/SKILL.md`.'
  echo "$SKILL_BLOCK_END"
}

# ---- Update CLAUDE.md ----

update_claude_md() {
  local skills_dir="$1"

  mkdir -p "$CLAUDE_DIR"

  if [ -f "$CLAUDE_MD" ]; then
    if grep -q "$SKILL_BLOCK_START" "$CLAUDE_MD"; then
      info "Updating existing skill block in $CLAUDE_MD..."
      temp_file=$(mktemp)
      awk "/$SKILL_BLOCK_START/{skip=1} /$SKILL_BLOCK_END/{skip=0; next} !skip" "$CLAUDE_MD" > "$temp_file"
      mv "$temp_file" "$CLAUDE_MD"
      # Remove trailing blank lines before appending
      while [ -s "$CLAUDE_MD" ] && [ -z "$(tail -c 1 "$CLAUDE_MD" | tr -d '\n')" ]; do
        truncate -s -1 "$CLAUDE_MD"
      done
      echo "" >> "$CLAUDE_MD"
      generate_skill_block "$skills_dir" >> "$CLAUDE_MD"
    else
      info "Appending skill block to existing $CLAUDE_MD..."
      echo "" >> "$CLAUDE_MD"
      generate_skill_block "$skills_dir" >> "$CLAUDE_MD"
    fi
  else
    info "Creating $CLAUDE_MD..."
    generate_skill_block "$skills_dir" > "$CLAUDE_MD"
  fi
}

# ---- Commands ----

cmd_install() {
  check_dependency git

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

  info "Making scripts executable..."
  find "$SKILLS_DIR" -name "*.sh" -exec chmod +x {} \;
  find "$SKILLS_DIR" -name "*.py" -exec chmod +x {} \;

  info "Scanning skills and updating Claude Code config..."
  update_claude_md "$SKILLS_DIR"

  print_result "installed"
}

cmd_update() {
  [ -d "$SKILLS_DIR/.git" ] || error "Skills not installed. Run 'bash install.sh' first."

  check_dependency git

  info "Pulling latest changes..."
  git -C "$SKILLS_DIR" pull origin main 2>/dev/null \
    || git -C "$SKILLS_DIR" pull origin master 2>/dev/null \
    || warn "Could not pull latest changes. Using existing version."

  info "Making scripts executable..."
  find "$SKILLS_DIR" -name "*.sh" -exec chmod +x {} \;
  find "$SKILLS_DIR" -name "*.py" -exec chmod +x {} \;

  info "Re-scanning skills and updating Claude Code config..."
  update_claude_md "$SKILLS_DIR"

  print_result "updated"
}

# ---- Output ----

print_result() {
  local action="$1"
  local count=0
  for f in "$SKILLS_DIR"/*/SKILL.md; do
    [ -f "$f" ] && count=$((count + 1))
  done

  echo ""
  echo "============================================"
  echo "  Antigravity Skills ${action} successfully"
  echo "============================================"
  echo ""
  echo "  Skills directory : $SKILLS_DIR"
  echo "  Skills found     : $count"
  echo "  Claude config    : $CLAUDE_MD"
  echo ""
  echo "  Commands:"
  echo "    bash ~/Skills/install.sh            # reinstall"
  echo "    bash ~/Skills/install.sh --update   # update"
  echo ""
  echo "============================================"
}

# ---- Main ----

case "${1:-}" in
  --update|-u)
    cmd_update
    ;;
  *)
    cmd_install
    ;;
esac
