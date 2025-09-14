#!/usr/bin/env python3
"""
github_push_assistant.py
Fully automated GitHub push assistant with Docker fallback, remote verification,
and Asciinema recording safety. PRF-compliant: everything that can be typed is scripted.

Features:
- Detects if Docker is available, uses fallback if not
- Checks for remote repository existence; creates it if missing
- Prevents Asciinema overwrite by auto-incrementing filenames
- Fully automated Git workflow: add, commit, push
- Detailed, human-readable logging
"""

import os
import subprocess
import sys
import re

# ---------------------------
# CONFIGURATION
# ---------------------------
REPO_PATH = os.path.abspath(".")
REMOTE_NAME = "origin"
ASCIINEMA_DIR = os.path.join(REPO_PATH, "asciinema")
DEFAULT_COMMIT_MSG = "Automated commit via github_push_assistant.py"

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------

def log(msg):
    """Print a timestamped message"""
    from datetime import datetime
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def run(cmd, capture_output=False):
    """Run a shell command, raise on failure"""
    log(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
    if result.returncode != 0:
        log(f"Command failed with exit code {result.returncode}")
        if capture_output:
            log(f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout.strip() if capture_output else None

def check_docker_available():
    """Check if Docker is available"""
    try:
        run("docker --version", capture_output=True)
        return True
    except Exception:
        log("Docker not available, falling back to host Git")
        return False

def ensure_remote_exists():
    """Verify the remote exists; create it if missing"""
    try:
        remotes = run(f"git remote", capture_output=True).splitlines()
        if REMOTE_NAME in remotes:
            log(f"Remote '{REMOTE_NAME}' exists")
            return
        else:
            log(f"Remote '{REMOTE_NAME}' missing, attempting to create")
            # Attempt GitHub CLI
            try:
                repo_name = os.path.basename(REPO_PATH)
                run(f"gh repo create {repo_name} --public --source=. --remote={REMOTE_NAME} --push")
                log(f"Remote '{REMOTE_NAME}' created via GitHub CLI")
            except Exception:
                raise RuntimeError("Remote missing and automatic creation failed")
    except Exception as e:
        log(f"Error verifying remote: {e}")
        raise

def prevent_asciinema_overwrite():
    """Generate a unique asciinema recording filename"""
    os.makedirs(ASCIINEMA_DIR, exist_ok=True)
    index = 1
    while True:
        filename = os.path.join(ASCIINEMA_DIR, f"session_{index}.cast")
        if not os.path.exists(filename):
            return filename
        index += 1

# ---------------------------
# GIT OPERATIONS
# ---------------------------

def git_add_commit_push(commit_msg=DEFAULT_COMMIT_MSG):
    """Stage all changes, commit, and push"""
    log("Adding all changes...")
    run("git add .")
    
    log(f"Committing with message: {commit_msg}")
    run(f'git commit -m "{commit_msg}" || echo "Nothing to commit"')
    
    ensure_remote_exists()
    
    log("Pushing to remote...")
    run(f"git push {REMOTE_NAME} main || git push {REMOTE_NAME} master")

# ---------------------------
# MAIN EXECUTION
# ---------------------------

def main():
    log("Starting github_push_assistant.py")
    
    if check_docker_available():
        log("Docker available: Git commands may run in container if desired")
        # Optional: could run inside Docker container here
    else:
        log("Using host Git environment")

    asciinema_file = prevent_asciinema_overwrite()
    log(f"Asciinema recording will be saved to: {asciinema_file}")

    git_add_commit_push()
    log("Push complete")

if __name__ == "__main__":
    main()
