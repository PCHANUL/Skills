#!/usr/bin/env python3
"""
Skill Manager CLI - A package manager for AI agent skills.

Usage:
    skill-manager install <github_url> [--local]
    skill-manager update [skill_name]
    skill-manager list
    skill-manager remove <skill_name>
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

# Default skills directory (global)
DEFAULT_SKILLS_DIR = os.path.expanduser("~/.skills")
LOCAL_SKILLS_DIR = ".skills"
MANIFEST_FILE = "skills.json"

def get_skills_dir(local=False):
    """Returns the appropriate skills directory."""
    if local and os.path.exists(LOCAL_SKILLS_DIR):
        return LOCAL_SKILLS_DIR
    elif local:
        os.makedirs(LOCAL_SKILLS_DIR, exist_ok=True)
        return LOCAL_SKILLS_DIR
    else:
        os.makedirs(DEFAULT_SKILLS_DIR, exist_ok=True)
        return DEFAULT_SKILLS_DIR

def get_manifest_path(skills_dir):
    return os.path.join(skills_dir, MANIFEST_FILE)

def load_manifest(skills_dir):
    manifest_path = get_manifest_path(skills_dir)
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            return json.load(f)
    return {"installed": {}}

def save_manifest(skills_dir, manifest):
    manifest_path = get_manifest_path(skills_dir)
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

def extract_skill_name(url):
    """Extracts skill name from GitHub URL."""
    # https://github.com/user/repo.git -> repo
    name = url.rstrip('/').rstrip('.git').split('/')[-1]
    return name

def install_skill(url, local=False):
    """Clones a skill repository from GitHub."""
    skills_dir = get_skills_dir(local)
    skill_name = extract_skill_name(url)
    skill_path = os.path.join(skills_dir, skill_name)
    
    if os.path.exists(skill_path):
        print(f"Skill '{skill_name}' already installed at {skill_path}.")
        print("Use 'skill-manager update' to update it.")
        return
    
    print(f"Installing '{skill_name}' from {url}...")
    result = subprocess.run(["git", "clone", url, skill_path], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error cloning repository: {result.stderr}")
        return
    
    # Update manifest
    manifest = load_manifest(skills_dir)
    manifest["installed"][skill_name] = {
        "url": url,
        "path": skill_path
    }
    save_manifest(skills_dir, manifest)
    
    print(f"✅ Successfully installed '{skill_name}' to {skill_path}")
    
    # Run index if available
    index_script = os.path.join(skill_path, "skill-manager", "scripts", "index_skills.py")
    if os.path.exists(index_script):
        print("Indexing skills...")
        subprocess.run(["python3", index_script, skill_path])

def update_skill(skill_name=None, local=False):
    """Updates installed skills by pulling latest changes."""
    skills_dir = get_skills_dir(local)
    manifest = load_manifest(skills_dir)
    
    if not manifest["installed"]:
        print("No skills installed.")
        return
    
    skills_to_update = [skill_name] if skill_name else list(manifest["installed"].keys())
    
    for name in skills_to_update:
        if name not in manifest["installed"]:
            print(f"Skill '{name}' not found.")
            continue
        
        skill_path = manifest["installed"][name]["path"]
        print(f"Updating '{name}'...")
        
        result = subprocess.run(
            ["git", "-C", skill_path, "pull", "origin", "main"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print(f"✅ '{name}' updated successfully.")
        else:
            # Try 'master' branch as fallback
            result = subprocess.run(
                ["git", "-C", skill_path, "pull", "origin", "master"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"✅ '{name}' updated successfully.")
            else:
                print(f"⚠️ Failed to update '{name}': {result.stderr}")

def list_skills(local=False):
    """Lists all installed skills."""
    # Check both global and local
    print("\n--- Installed Skills ---")
    
    for is_local, label in [(False, "Global (~/.skills)"), (True, "Local (.skills)")]:
        skills_dir = DEFAULT_SKILLS_DIR if not is_local else LOCAL_SKILLS_DIR
        if not os.path.exists(skills_dir):
            continue
        
        manifest = load_manifest(skills_dir)
        if manifest["installed"]:
            print(f"\n{label}:")
            for name, info in manifest["installed"].items():
                print(f"  🔹 {name}")
                print(f"      Source: {info['url']}")
    
    print("\n------------------------")

def remove_skill(skill_name, local=False):
    """Removes an installed skill."""
    skills_dir = get_skills_dir(local)
    manifest = load_manifest(skills_dir)
    
    if skill_name not in manifest["installed"]:
        print(f"Skill '{skill_name}' not found.")
        return
    
    skill_path = manifest["installed"][skill_name]["path"]
    
    confirm = input(f"Remove '{skill_name}' from {skill_path}? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    
    shutil.rmtree(skill_path, ignore_errors=True)
    del manifest["installed"][skill_name]
    save_manifest(skills_dir, manifest)
    
    print(f"✅ Removed '{skill_name}'.")

def main():
    parser = argparse.ArgumentParser(
        description="Skill Manager - A package manager for AI agent skills."
    )
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Install
    install_parser = subparsers.add_parser('install', help='Install a skill from GitHub')
    install_parser.add_argument('url', help='GitHub repository URL')
    install_parser.add_argument('--local', action='store_true', help='Install to local .skills directory')
    
    # Update
    update_parser = subparsers.add_parser('update', help='Update installed skills')
    update_parser.add_argument('skill_name', nargs='?', help='Specific skill to update (optional)')
    update_parser.add_argument('--local', action='store_true', help='Update local skills')
    
    # List
    list_parser = subparsers.add_parser('list', help='List installed skills')
    
    # Remove
    remove_parser = subparsers.add_parser('remove', help='Remove a skill')
    remove_parser.add_argument('skill_name', help='Skill name to remove')
    remove_parser.add_argument('--local', action='store_true', help='Remove from local directory')
    
    args = parser.parse_args()
    
    if args.command == 'install':
        install_skill(args.url, args.local)
    elif args.command == 'update':
        update_skill(args.skill_name, getattr(args, 'local', False))
    elif args.command == 'list':
        list_skills()
    elif args.command == 'remove':
        remove_skill(args.skill_name, args.local)

if __name__ == "__main__":
    main()
