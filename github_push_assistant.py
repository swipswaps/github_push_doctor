#!/usr/bin/env python3
"""
GitHub Push Assistant for flowCFD (Docker-ready)
================================================
Interactive, robust assistant to push any folder to GitHub.
- Saves configuration to github_push_config.yaml
- Detects dependencies: PyYAML, gh CLI, asciinema
- Enhanced logging, error reporting, and UX
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Optional YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

CONFIG_FILE = "github_push_config.yaml"
LOG_FILE = "github_push_assistant.log"

# ----------------------
# ANSI colors for terminal
# ----------------------
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

# ----------------------
# Logging function (tee style)
# ----------------------
def log(message, level="INFO"):
    """Log to stdout and append to LOG_FILE"""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{level}] {message}\n")
    print(message)

# ----------------------
# System command execution
# ----------------------
def run_command(command, check=True, capture_output=True):
    """Run a system command with output logging"""
    log(f"$ {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=capture_output,
            check=check
        )
        if capture_output:
            if result.stdout.strip():
                log(result.stdout.strip(), "OUTPUT")
            if result.stderr.strip():
                log(result.stderr.strip(), "ERROR")
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {e}", "ERROR")
        if e.stdout:
            log(e.stdout, "OUTPUT")
        if e.stderr:
            log(e.stderr, "ERROR")
        return False, e.stdout, e.stderr

# ----------------------
# User input and confirmation
# ----------------------
def get_user_input(prompt, default=None):
    if default:
        value = input(f"{prompt} [{default}]: ").strip()
        return value if value else default
    else:
        return input(f"{prompt}: ").strip()

def confirm_action(message):
    while True:
        resp = input(f"{message} (y/n): ").strip().lower()
        if resp in ["y","yes"]:
            return True
        elif resp in ["n","no"]:
            return False
        else:
            log("Please enter 'y' or 'n'.")

# ----------------------
# Dependency checks
# ----------------------
def check_git():
    ok, _, _ = run_command("git --version", check=False)
    if ok:
        log("Git is installed.", "SUCCESS")
    else:
        log("Git not found. Install git first.", "ERROR")
    return ok

def check_gh():
    ok, _, _ = run_command("gh --version", check=False)
    if ok:
        log("GitHub CLI detected.", "SUCCESS")
    else:
        log("GitHub CLI not found. Install gh CLI for automated remote creation.", "WARNING")
    return ok

def check_asciinema():
    if shutil.which("asciinema"):
        log("Asciinema detected.", "SUCCESS")
        return True
    else:
        log("Asciinema not found. Recording disabled.", "WARNING")
        return False

def check_pyyaml():
    if YAML_AVAILABLE:
        log(f"PyYAML detected.", "SUCCESS")
        return True
    else:
        log(f"PyYAML >=6.0 not installed. YAML persistence disabled.", "WARNING")
        return False

# ----------------------
# Configuration management
# ----------------------
def load_config():
    if check_pyyaml() and Path(CONFIG_FILE).exists():
        try:
            with open(CONFIG_FILE,"r") as f:
                config = yaml.safe_load(f) or {}
            log(f"Loaded config from {CONFIG_FILE}")
            return config
        except Exception as e:
            log(f"Failed to load config: {e}", "ERROR")
            return {}
    else:
        return {}

def save_config(config):
    if check_pyyaml():
        try:
            with open(CONFIG_FILE,"w") as f:
                yaml.safe_dump(config,f)
            log(f"Saved config to {CONFIG_FILE}")
        except Exception as e:
            log(f"Failed to save config: {e}", "ERROR")

# ----------------------
# Main workflow
# ----------------------
def main():
    log(f"{Colors.BOLD}{Colors.GREEN}🔧 GitHub Push Assistant{Colors.END}")

    # Load previous configuration
    config = load_config()
    
    # Step 1: Select project folder
    default_path = config.get("project_path", str(Path.cwd()))
    project_path = get_user_input("Project path", default_path)
    project_path = str(Path(project_path).resolve())
    log(f"Working in: {project_path}")
    config["project_path"] = project_path
    
    os.chdir(project_path)

    # Step 2: Check git, gh, asciinema
    if not check_git():
        return False
    gh_installed = check_gh()
    asciinema_installed = check_asciinema()
    
    # Step 3: GitHub authentication
    if gh_installed:
        ok, _, _ = run_command("gh auth status", check=False)
        if not ok:
            if confirm_action("gh CLI not authenticated. Run 'gh auth login'?"):
                run_command("gh auth login")
    
    # Step 4: Determine repo name
    default_repo = config.get("repo_name", Path(project_path).name)
    repo_name = get_user_input("GitHub repo name", default_repo)
    config["repo_name"] = repo_name

    # Step 5: Default branch
    default_branch = config.get("default_branch","main")
    branch_name = get_user_input("Default branch", default_branch)
    config["default_branch"] = branch_name

    # Step 6: Commit message
    default_commit = config.get("commit_message","update project")
    commit_msg = get_user_input("Commit message", default_commit)
    config["commit_message"] = commit_msg

    # Save current config
    save_config(config)

    # Step 7: Initialize repo if needed
    if not (Path(".git").exists()):
        log("⚙️ Initializing new git repo...")
        run_command("git init")
        run_command(f"git branch -M {branch_name}")

    # Step 8: Stage all files
    log("➕ Staging all files...")
    run_command("git add .")

    # Step 9: Commit changes
    log("💬 Committing...")
    run_command(f'git commit -m "{commit_msg}"', check=False)

    # Step 10: Create GitHub repo if gh CLI present
    if gh_installed:
        log(f"🌐 Creating GitHub repo {repo_name}...")
        run_command(f"gh repo create {repo_name} --source=. --public --push", check=False)

    log(f"{Colors.GREEN}✅ Push workflow complete. Review logs and GitHub repo.{Colors.END}")
    return True

# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("User cancelled.", "WARNING")
        sys.exit(1)
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)
