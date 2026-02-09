import argparse
import subprocess
import sys
import os
import json

def run_command(cmd_list):
    """Runs a shell command and returns output (string), or None on failure."""
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running {' '.join(cmd_list)}: {e.stderr}")
        return None

def fetch_changed_files(pr_number):
    """
    Returns a list of changed file paths for the given PR.
    """
    # Create temp files for PR content
    # For simplicity, we just list files here. 
    # In a real pipeline, we'd need to fetch the diff or use `gh pr view --json files`
    output = run_command(['gh', 'pr', 'view', str(pr_number), '--json', 'files', '--jq', '.files[].path'])
    if not output:
        return []
    return output.splitlines()

def fetch_full_content(file_path):
    """
    Reads the full content of a file from the local checkout (assuming branch checked out).
    If file doesn't exist (deleted), returns empty string.
    """
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]"

def run_linter():
    """
    Detects language and runs appropriate linter.
    Currently supports Dart/Flutter.
    Returns linter output string.
    """
    output = ""
    # Check for pubspec.yaml -> Flutter/Dart
    if os.path.exists('pubspec.yaml'):
        print("Detected Flutter/Dart project. Running `flutter analyze`...")
        try:
            # capture_output=True creates a completed process object
            proc = subprocess.run(['flutter', 'analyze'], capture_output=True, text=True)
            output += f"--- Flutter Analyze Output ---\n{proc.stdout}\n{proc.stderr}\n"
        except FileNotFoundError:
            output += "Error: `flutter` command not found.\n"
    
    # Add more linters here (e.g., eslint for JS)
    
    return output

def load_conventions():
    """
    Tries to load `docs/CONVENTIONS.md`. If not found, returns generic advice.
    """
    conventions_path = "docs/CONVENTIONS.md"
    if os.path.exists(conventions_path):
        try:
            with open(conventions_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            pass
    return "Standard Clean Code principles (DRY, SOLID, Clear Naming)."

def analyze_pr(pr_number):
    print(f"Starting QA Analysis for PR #{pr_number}...")

    # 1. Provide Context: Changed Files
    changed_files = fetch_changed_files(pr_number)
    if not changed_files:
        print("No changed files found or error fetching PR details.")
        return

    # 2. Provide Context: Diff & Full Content
    # We construct a prompt for the Agent.
    prompt_context = f"# Code Review Context for PR #{pr_number}\n\n"
    
    # 3. Linter Results
    linter_output = run_linter()
    prompt_context += f"## Linter Results\n```\n{linter_output}\n```\n\n"

    # 4. Conventions
    conventions = load_conventions()
    prompt_context += f"## Project Conventions\n{conventions}\n\n"
    
    prompt_context += "## File Changes Analysis\n"

    for file_path in changed_files:
        # Ignore non-code files (images, locks)
        if file_path.endswith(('.png', '.jpg', '.lock', '.resolved')):
            continue
            
        full_content = fetch_full_content(file_path)
        
        prompt_context += f"\n### File: {file_path}\n"
        prompt_context += "#### Full Content (for context):\n"
        prompt_context += f"```\n{full_content}\n```\n"
        
        # In a real advanced script, we might include specific diff chunks here too.
        # But for Agent use, Full Content is often more valuable for logic checks.

    print("\n" + "="*50)
    print("READY FOR AGNET REVIEW")
    print("="*50)
    print("The following is the structured context for the PR Review.")
    print("AGENT: Please read this output, analyze the code against the conventions, and perform `gh pr review`.")
    print("-" * 50)
    print(prompt_context)
    print("-" * 50)


def main():
    parser = argparse.ArgumentParser(description='Automated QA & Code Review Helper')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Fetch context and prepare review prompt')
    analyze_parser.add_argument('--pr', type=int, required=True, help='PR number')

    args = parser.parse_args()

    if args.command == 'analyze':
        analyze_pr(args.pr)

if __name__ == "__main__":
    main()
