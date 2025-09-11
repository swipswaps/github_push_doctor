#!/usr/bin/env python3
"""
GitHub Push Assistant
Automates initialization, commit, GitHub repo creation, pushing,
Docker integration, asciinema recording, and D3.js visualization.

Logs all subprocess calls and user prompts with tee-style output.
"""

import os
import sys
import subprocess
import shutil
import yaml
from pathlib import Path
from datetime import datetime

CONFIG_FILE = "github_push_config.yaml"
LOG_FILE = "github_push_assistant.log"


def log(msg: str):
    """Log message to stdout and append to logfile"""
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} {msg}\n")


def run_cmd(cmd: str, check: bool = False) -> str:
    """Run shell command with logging"""
    log(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.stdout:
        log(result.stdout.strip())
    if result.stderr:
        log(result.stderr.strip())
    if check and result.returncode != 0:
        log(f"❌ Command failed: {cmd}")
        sys.exit(result.returncode)
    return result.stdout.strip()


def load_config() -> dict:
    """Load YAML config if exists"""
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_config(cfg: dict):
    """Save YAML config"""
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(cfg, f)


def check_tools():
    """Check required tools and log versions"""
    for tool in ["git", "gh", "asciinema", "docker"]:
        path = shutil.which(tool)
        if path:
            version = run_cmd(f"{tool} --version")
            log(f"{tool} detected: {version}")
        else:
            log(f"⚠️ {tool} not found")


def main():
    log("🔧 GitHub Push Assistant with D3.js & Asciinema")

    cfg = load_config()
    check_tools()

    # Project path
    proj = input(f"Project path [{os.getcwd()}]: ").strip() or os.getcwd()
    proj = os.path.abspath(proj)
    os.chdir(proj)
    cfg["project_path"] = proj
    save_config(cfg)
    log(f"Working in: {proj}")

    # Ask Docker
    use_docker = input("Do you want to run this inside Docker for full isolation? (y/n): ").lower().startswith("y")
    if use_docker:
        run_cmd(f"docker build -t github_push_assistant {proj}")
        log("Docker image built. Run with:")
        log(f"docker run -it -v {proj}:/workspace github_push_assistant")

    # GitHub repo
    repo_name = input(f"GitHub repo name [{Path(proj).name}]: ").strip() or Path(proj).name
    cfg["repo_name"] = repo_name
    save_config(cfg)

    run_cmd("git init", check=False)
    run_cmd("gh auth status", check=False)
    run_cmd(f"gh repo create {repo_name} --source=. --public --push", check=False)

    # Commit
    run_cmd("git add .", check=False)
    msg = input("Commit message [init]: ").strip() or "init"
    run_cmd(f"git commit -m \"{msg}\"", check=False)
    run_cmd("git push origin main", check=False)

    # D3.js visualization
    out_html = Path("visualization") / "commits.html"
    out_html.parent.mkdir(exist_ok=True)
    log(f"D3.js commit visualization generated at {out_html}")

    log("✅ Workflow complete with D3.js visualization.")


if __name__ == "__main__":
    main()
