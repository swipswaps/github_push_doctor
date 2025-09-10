#!/usr/bin/env python3
"""
GitHub Push Assistant with Persistent Config
--------------------------------------------
- Guides user through staging, committing, and pushing to GitHub
- Persists preferences in github_push_config.yaml
- Reloads config each run with editable defaults
- Supports auto mode (--auto) for unattended pushes
"""

import subprocess
import sys
import shutil
import argparse
from pathlib import Path

# Try to load YAML support
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

CONFIG_FILE = Path("github_push_config.yaml")


def run_cmd(cmd, check=True, capture=False):
    """Run shell command safely."""
    try:
        if capture:
            return subprocess.check_output(cmd, text=True).strip()
        else:
            subprocess.run(cmd, check=check)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}\n{e}")
        sys.exit(1)


def ensure_dependency(tool):
    """Check that a dependency is installed."""
    if shutil.which(tool) is None:
        print(f"❌ Required tool '{tool}' not found in PATH. Please install it.")
        sys.exit(1)


def load_config():
    """Load config file if available."""
    if CONFIG_FILE.exists() and HAS_YAML:
        try:
            with open(CONFIG_FILE, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Failed to load config ({e}), starting fresh.")
            return {}
    return {}


def save_config(config):
    """Save config back to YAML."""
    if HAS_YAML:
        with open(CONFIG_FILE, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False)
    else:
        print("⚠️ PyYAML not installed. Config will not persist.")


def prompt(msg, default=None):
    """Prompt user with default option."""
    if default:
        full = f"{msg} [{default}]: "
    else:
        full = f"{msg}: "
    ans = input(full).strip()
    return ans if ans else default


def main():
    parser = argparse.ArgumentParser(description="GitHub Push Assistant")
    parser.add_argument("--auto", action="store_true", help="Run non-interactively using saved config")
    args = parser.parse_args()

    # Ensure tools available
    ensure_dependency("git")
    ensure_dependency("gh")

    config = load_config()

    # Interactive mode
    if not args.auto:
        print("\n🔧 GitHub Push Assistant\n")

        project_path = prompt("Project path", config.get("project_path", str(Path.cwd())))
        repo_name = prompt("GitHub repo name", config.get("repo_name", Path(project_path).name))
        default_branch = prompt("Default branch", config.get("default_branch", "main"))
        commit_message = prompt("Commit message", config.get("commit_message", "update project"))

        config.update({
            "project_path": project_path,
            "repo_name": repo_name,
            "default_branch": default_branch,
            "commit_message": commit_message,
        })

        save_config(config)
    else:
        if not config:
            print("❌ No config found. Run interactively first.")
            sys.exit(1)

        project_path = config["project_path"]
        repo_name = config["repo_name"]
        default_branch = config["default_branch"]
        commit_message = config["commit_message"]

    # Change to project path
    project_path = Path(project_path).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Project path not found: {project_path}")
        sys.exit(1)
    print(f"\n📂 Working in: {project_path}")
    os_cwd = Path.cwd()
    import os
    os.chdir(project_path)

    # Init repo if missing
    if not (project_path / ".git").exists():
        print("⚙️ Initializing new git repo...")
        run_cmd(["git", "init", "-b", default_branch])

    # Stage changes
    print("➕ Staging changes...")
    run_cmd(["git", "add", "."])

    # Commit
    print("💬 Committing...")
    run_cmd(["git", "commit", "-m", commit_message], check=False)

    # Check if remote exists
    remotes = run_cmd(["git", "remote"], capture=True).splitlines()
    if "origin" not in remotes:
        print(f"🌐 Creating remote repo {repo_name} on GitHub...")
        run_cmd(["gh", "repo", "create", repo_name, "--source=.", "--public", "--push"])

    # Push
    print("🚀 Pushing to GitHub...")
    run_cmd(["git", "push", "-u", "origin", default_branch])

    # Restore working dir
    os.chdir(os_cwd)

    print("\n✅ Done! Your project is now on GitHub.")


if __name__ == "__main__":
    main()
