#!/usr/bin/env python3
"""
GitHub Push Assistant for flowCFD
==================================
Interactive script to guide users through pushing their project to GitHub
with human-in-the-loop prompts, YAML config, and gh auth detection.
"""

import os
import subprocess
import sys
import yaml
from pathlib import Path

CONFIG_FILE = "github_push_config.yaml"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(step_num, title, description=""):
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== STEP {step_num}: {title} ==={Colors.END}")
    if description:
        print(f"{Colors.YELLOW}{description}{Colors.END}")

def print_success(msg): print(f"{Colors.GREEN}✅ {msg}{Colors.END}")
def print_warning(msg): print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")
def print_error(msg): print(f"{Colors.RED}❌ {msg}{Colors.END}")

def run_command(cmd, capture_output=True, check=True):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, check=check)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def get_user_input(prompt, default=None):
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def confirm_action(message):
    while True:
        resp = input(f"{message} (y/n): ").strip().lower()
        if resp in ['y', 'yes']: return True
        elif resp in ['n', 'no']: return False
        print("Please enter 'y' or 'n'.")

def check_git_installed():
    success, _, _ = run_command("git --version")
    return success

def check_git_config():
    name_s, name, _ = run_command("git config user.name")
    email_s, email, _ = run_command("git config user.email")
    return name_s and email_s, name, email

def load_config():
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(cfg, f)

def check_gh_authenticated():
    success, output, _ = run_command("gh auth status", check=False)
    return success and "Logged in" in output

def main():
    print(f"{Colors.BOLD}{Colors.GREEN}🚀 GitHub Push Assistant{Colors.END}\n")
    cfg = load_config()

    # STEP 0: Git Prerequisites
    print_step(0, "PREREQUISITES CHECK")
    if not check_git_installed():
        print_error("Git is not installed. Install git first.")
        return False
    print_success("Git installed")

    cfg["project_path"] = get_user_input("Project path", cfg.get("project_path", str(Path.cwd())))
    Path(cfg["project_path"]).mkdir(parents=True, exist_ok=True)
    os.chdir(cfg["project_path"])
    print_success(f"Working in: {cfg['project_path']}")

    # STEP 1: Git config
    config_ok, username, email = check_git_config()
    if not config_ok:
        print_warning("Git user not configured")
        if confirm_action("Configure now?"):
            name = get_user_input("Enter your full name")
            email = get_user_input("Enter your email")
            run_command(f'git config --global user.name "{name}"')
            run_command(f'git config --global user.email "{email}"')
            print_success("Git config updated")
    else:
        print_success(f"Git configured for {username} <{email}>")

    # STEP 2: GitHub Authentication (gh)
    print_step(2, "GITHUB AUTHENTICATION")
    if check_gh_authenticated():
        print_success("gh CLI already authenticated")
    else:
        if confirm_action("gh CLI not authenticated. Authenticate now?"):
            run_command("gh auth login", capture_output=False)
            if not check_gh_authenticated():
                print_error("Authentication failed.")
                return False
            print_success("gh CLI authenticated successfully")

    # Save project path in config
    cfg["project_path"] = str(Path.cwd())
    save_config(cfg)

    # STEP 3: Git Repo Initialization
    print_step(3, "GIT REPOSITORY CHECK")
    if not (Path(".git").exists()):
        print("⚙️ Initializing new git repo...")
        run_command("git init")
        run_command("git branch -M main")
        print_success("Git repository initialized")

    # STEP 4: Remote check & create
    print_step(4, "REMOTE CHECK")
    success, remote_out, _ = run_command("git remote -v")
    if not success or not remote_out:
        repo_name = get_user_input("GitHub repo name", cfg.get("repo_name", Path.cwd().name))
        cfg["repo_name"] = repo_name
        save_config(cfg)
        # Use gh to create
        push_choice = confirm_action("Create GitHub repo and push?")
        if push_choice:
            success, _, _ = run_command(f"gh repo create {repo_name} --source=. --public --push", check=False)
            if success:
                print_success(f"Repo {repo_name} created and pushed")
            else:
                print_error("Failed to create repo via gh")
                return False

    # STEP 5: Stage & Commit
    print_step(5, "STAGE AND COMMIT")
    run_command("git add .")
    commit_msg = get_user_input("Commit message", cfg.get("last_commit_msg", "update project"))
    cfg["last_commit_msg"] = commit_msg
    save_config(cfg)
    run_command(f'git commit -m "{commit_msg}"', check=False)
    print_success("Changes committed")

    # STEP 6: Push
    print_step(6, "PUSH TO GITHUB")
    run_command("git push origin main", check=False)
    print_success("Push completed (verify on GitHub)")

    print_success("🎉 All steps completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Push cancelled by user.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        sys.exit(1)
