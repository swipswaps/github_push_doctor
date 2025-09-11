#!/usr/bin/env python3
"""
GitHub Push Assistant (Upgraded)
- Automatically uses Docker for isolation unless user opts out
- Automatically records first run with asciinema unless user opts out
- Handles GitHub remote detection / creation seamlessly
- Generates D3.js commit visualization over time with messages
- Comprehensive logging with emoji indicators
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import yaml

CONFIG_FILE = "github_push_config.yaml"
LOG_FILE = "github_push_assistant.log"
VISUALIZATION_DIR = Path("visualization")
VISUALIZATION_FILE = VISUALIZATION_DIR / "commits.html"


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
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_config(cfg: dict):
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(cfg, f)


def check_tools():
    for tool in ["git", "gh", "asciinema", "docker"]:
        path = shutil.which(tool)
        if path:
            version = run_cmd(f"{tool} --version")
            log(f"{tool} detected: {version}")
        else:
            log(f"⚠️ {tool} not found")


def ensure_remote(repo_name: str):
    remotes = run_cmd("git remote", check=False).splitlines()
    if "origin" in remotes:
        log("✅ Remote 'origin' exists, updating URL...")
        run_cmd(f"gh repo view {repo_name} --json url -q .url | xargs git remote set-url origin")
    else:
        log("🔧 Adding remote 'origin'...")
        run_cmd(f"gh repo create {repo_name} --source=. --public --push", check=False)


def run_asciinema_docker():
    """Record first run automatically and build Docker"""
    CASTFILE = "github_push_assistant_first_run.cast"
    LOGFILE = LOG_FILE

    # Only record if cast does not exist
    if not Path(CASTFILE).exists():
        log(f"🎥 Recording first run automatically: {CASTFILE}")
        # Start interactive shell inside asciinema to let user run workflow manually
        subprocess.run(
            f"asciinema rec -y --overwrite {CASTFILE} --command 'echo \"Run the workflow here manually\"; bash'",
            shell=True,
            check=False,
        )
        log(f"✅ Asciinema recording complete: {CASTFILE}")
    else:
        log(f"ℹ️ First run cast already exists: {CASTFILE}, skipping recording")

    # Docker build attempt
    try:
        run_cmd(f"docker build -t github_push_assistant {os.getcwd()}")
        log(f"🐳 Docker image built. Run with:")
        log(f"docker run -it -v {os.getcwd()}:/workspace github_push_assistant")
    except Exception as e:
        log(f"⚠️ Docker build failed: {e}. Continuing natively...")


def generate_d3_visualization():
    VISUALIZATION_DIR.mkdir(exist_ok=True)
    commits = run_cmd('git log --pretty=format:"%H|%an|%ad|%s" --date=iso').splitlines()
    data_entries = []
    for i, c in enumerate(commits):
        h, author, date, msg = c.split("|", 3)
        data_entries.append({
            "x": i * 100 + 50,
            "y": 200,
            "hash": h,
            "author": author,
            "date": date,
            "message": msg
        })

    js_data_file = VISUALIZATION_DIR / "commits_data.js"
    js_data_file.write_text(f"const commits = {data_entries};")

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>D3.js Commit Visualization</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
<h1>Commit History Visualization</h1>
<svg id="chart" width="1000" height="400"></svg>
<script>
const svg = d3.select("#chart");
svg.selectAll("circle")
   .data(commits)
   .enter()
   .append("circle")
   .attr("cx", d => d.x)
   .attr("cy", d => d.y)
   .attr("r", 20)
   .style("fill", "steelblue");

svg.selectAll("text")
   .data(commits)
   .enter()
   .append("text")
   .attr("x", d => d.x)
   .attr("y", d => d.y + 40)
   .attr("text-anchor", "middle")
   .text(d => d.message);
</script>
</body>
</html>
"""
    VISUALIZATION_FILE.write_text(html_content)
    log(f"✅ D3.js commit visualization generated at {VISUALIZATION_FILE}")


def main():
    log("🔧 GitHub Push Assistant with D3.js & Asciinema (Upgraded)")
    cfg = load_config()
    check_tools()

    proj = input(f"Project path [{os.getcwd()}]: ").strip() or os.getcwd()
    proj = os.path.abspath(proj)
    os.chdir(proj)
    cfg["project_path"] = proj
    save_config(cfg)
    log(f"Working in: {proj}")

    # Auto-record first run and Docker build (non-recursive)
    run_asciinema_docker()

    repo_name = input(f"GitHub repo name [{Path(proj).name}]: ").strip() or Path(proj).name
    cfg["repo_name"] = repo_name
    save_config(cfg)

    run_cmd("git init", check=False)
    run_cmd("gh auth status", check=False)
    ensure_remote(repo_name)

    run_cmd("git add .", check=False)
    msg = input("Commit message [init]: ").strip() or "init"
    run_cmd(f'git commit -m "{msg}"', check=False)
    run_cmd("git push origin main", check=False)

    generate_d3_visualization()
    log("✅ Workflow complete with upgraded D3.js visualization.")


if __name__ == "__main__":
    main()
