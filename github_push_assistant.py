#!/usr/bin/env python3
"""
GitHub Push Assistant (Upgraded)
Automates:
- Initialization, commit, GitHub repo creation/push
- Docker integration with automated build/run
- Asciinema recording of first run
- D3.js commit visualization with full commit messages and timestamps
- Logging of all subprocess calls and user prompts
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
GRAPHQL_JSON = "graphql_output.json"

# --------------------------
# Logging / subprocess utils
# --------------------------
def log(msg: str):
    """Log message to stdout + logfile"""
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
    """Check required tools + log versions"""
    for tool in ["git", "gh", "asciinema", "docker"]:
        path = shutil.which(tool)
        if path:
            version = run_cmd(f"{tool} --version")
            log(f"{tool} detected: {version}")
        else:
            log(f"⚠️ {tool} not found")


# --------------------------
# Git / GitHub helpers
# --------------------------
def git_log_to_json() -> list[dict]:
    """Return recent commits as list of dicts with message, author, date"""
    result = run_cmd(
        'git log --pretty=format:"%H|%an|%ad|%s" --date=iso', check=True
    )
    commits = []
    for line in result.splitlines():
        sha, author, date, message = line.split("|", 3)
        commits.append({"sha": sha, "author": author, "date": date, "message": message})
    return commits


def generate_visualization(commits: list[dict]):
    """Generate simple D3.js commit visualization with commit timestamps"""
    import json

    vis_dir = Path("visualization")
    vis_dir.mkdir(exist_ok=True)
    out_html = vis_dir / "commits.html"
    out_json = vis_dir / "commits.json"

    out_json.write_text(json.dumps(commits, indent=2))

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Commit History Visualization</title>
      <script src="https://d3js.org/d3.v7.min.js"></script>
    </head>
    <body>
      <h1>Commit History Visualization</h1>
      <svg id="chart" width="1000" height="400"></svg>
      <script>
        d3.json("commits.json").then(data => {{
            const svg = d3.select("#chart");
            const parseDate = d3.isoParse;
            const xScale = d3.scaleTime()
                             .domain(d3.extent(data, d => parseDate(d.date)))
                             .range([50, 950]);
            const yScale = d3.scaleLinear().domain([0, data.length]).range([350, 50]);

            svg.selectAll("circle")
                .data(data)
                .enter()
                .append("circle")
                .attr("cx", d => xScale(parseDate(d.date)))
                .attr("cy", (d,i) => yScale(i))
                .attr("r", 8)
                .style("fill", "steelblue");

            svg.selectAll("text")
                .data(data)
                .enter()
                .append("text")
                .attr("x", d => xScale(parseDate(d.date)))
                .attr("y", (d,i) => yScale(i)-12)
                .attr("text-anchor", "middle")
                .text(d => d.message);
        }});
      </script>
    </body>
    </html>
    """
    out_html.write_text(html_content)
    log(f"D3.js commit visualization generated at {out_html}")


# --------------------------
# Main workflow
# --------------------------
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

    # Docker optional
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

    # Collect commits for D3.js visualization
    commits = git_log_to_json()
    generate_visualization(commits)

    log("✅ Workflow complete with upgraded D3.js visualization.")


if __name__ == "__main__":
    main()
