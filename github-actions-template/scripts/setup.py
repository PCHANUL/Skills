"""
GitHub Actions Workflow Installer

Copies the project-workflow GitHub Actions templates into a target repository's
.github/workflows/ directory.

Usage:
    python3 setup.py --repo /path/to/your/repo
    python3 setup.py --repo /path/to/your/repo --workflows project-drive pr-review
"""

import argparse
import os
import shutil
import sys

AVAILABLE_WORKFLOWS = {
    "project-setup": "project-setup.yml",
    "project-drive": "project-drive.yml",
    "pr-review": "pr-review.yml",
}


def get_workflows_dir():
    """Returns the path to the workflows directory relative to this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(script_dir), "workflows")


def install_workflows(repo_path, workflow_names=None):
    """Copies workflow files to the target repository."""
    workflows_src = get_workflows_dir()

    if not os.path.isdir(workflows_src):
        print(f"Error: Workflows source directory not found: {workflows_src}")
        sys.exit(1)

    if not os.path.isdir(repo_path):
        print(f"Error: Repository path not found: {repo_path}")
        sys.exit(1)

    # Determine which workflows to install
    if workflow_names:
        selected = {}
        for name in workflow_names:
            if name in AVAILABLE_WORKFLOWS:
                selected[name] = AVAILABLE_WORKFLOWS[name]
            else:
                print(f"Warning: Unknown workflow '{name}'. Skipping.")
                print(f"  Available: {', '.join(AVAILABLE_WORKFLOWS.keys())}")
        if not selected:
            print("Error: No valid workflows selected.")
            sys.exit(1)
    else:
        selected = AVAILABLE_WORKFLOWS

    # Create .github/workflows/ in target repo
    target_dir = os.path.join(repo_path, ".github", "workflows")
    os.makedirs(target_dir, exist_ok=True)

    print(f"Installing workflows to: {target_dir}")
    print()

    for name, filename in selected.items():
        src = os.path.join(workflows_src, filename)
        dst = os.path.join(target_dir, filename)

        if not os.path.exists(src):
            print(f"  Warning: Source file not found: {src}. Skipping '{name}'.")
            continue

        if os.path.exists(dst):
            print(f"  [{name}] Overwriting existing {filename}")
        else:
            print(f"  [{name}] Installing {filename}")

        shutil.copy2(src, dst)

    print()
    print("Installation complete!")
    print()
    print("Next steps:")
    print("  1. Add ANTHROPIC_API_KEY to your repository secrets")
    print("     (Settings > Secrets and variables > Actions > New repository secret)")
    print()
    print("  2. Commit and push the workflow files:")
    print(f"     cd {repo_path}")
    print("     git add .github/workflows/")
    print('     git commit -m "ci: Add project-workflow GitHub Actions"')
    print("     git push")
    print()
    print("  3. Go to GitHub Actions tab to trigger workflows manually.")


def list_workflows():
    """Lists all available workflow templates."""
    print("Available workflow templates:")
    print()
    for name, filename in AVAILABLE_WORKFLOWS.items():
        print(f"  {name:20s} -> {filename}")
    print()
    print("Use --workflows to select specific ones, or omit to install all.")


def main():
    parser = argparse.ArgumentParser(
        description="Install GitHub Actions workflow templates into a repository."
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="Path to the target repository",
    )
    parser.add_argument(
        "--workflows",
        nargs="*",
        help="Specific workflows to install (default: all)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available workflow templates",
    )

    args = parser.parse_args()

    if args.list:
        list_workflows()
        return

    if not args.repo:
        parser.print_help()
        print()
        list_workflows()
        return

    install_workflows(args.repo, args.workflows)


if __name__ == "__main__":
    main()
