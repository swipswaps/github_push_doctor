#!/usr/bin/env python3
"""
GitHub Push Assistant with D3.js Visualization, Asciinema Recording, and Docker Wrapper
=======================================================================================
- Automatic dependency management (Git, Python packages, gh CLI, asciinema, Docker)
- YAML config persistence (`github_push_config.yaml`)
- Docker optional for isolation
- D3.js interactive commit visualization
- Tee-style logging
- Human-in-the-loop interaction
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

CONFIG_FILE = "github_push_config.yaml"
LOG_FILE = "github_push_assistant.log"
VIS_DIR = "visualization"
FIRST_RUN_CAST = "github_push_assistant_first_run.cast"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log(msg, color=None):
    prefix = color if color else ""
    print(f"{prefix}{msg}{Colors.END if color else ''}")
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def run_command(cmd, capture_output=True, check=True, tee=True):
    log(f"$ {cmd}", Colors.BLUE)
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            check=check
        )
        output = result.stdout.strip() if result.stdout else ""
        error = result.stderr.strip() if result.stderr else ""
        if tee:
            if output:
                log(output)
            if error:
                log(error, Colors.RED)
        return True, output, error
    except subprocess.CalledProcessError as e:
        if tee:
            log(e.stdout if e.stdout else "", Colors.YELLOW)
            log(e.stderr if e.stderr else "", Colors.RED)
        return False, e.stdout, e.stderr

def get_input(prompt, default=None):
    if default:
        inp = input(f"{prompt} [{default}]: ").strip()
        return inp if inp else default
    else:
        return input(f"{prompt}: ").strip()

def confirm(msg):
    while True:
        resp = input(f"{msg} (y/n): ").strip().lower()
        if resp in ["y", "yes"]:
            return True
        elif resp in ["n", "no"]:
            return False

def check_and_install_dependencies():
    # Git
    success, git_ver, _ = run_command("git --version")
    if success:
        log(f"Git detected: {git_ver}", Colors.GREEN)
    else:
        log("Git not found. Please install git first.", Colors.RED)
        sys.exit(1)

    # gh CLI
    success, gh_ver, _ = run_command("gh --version")
    if success:
        log(f"GitHub CLI detected: {gh_ver}", Colors.GREEN)
    else:
        log("GitHub CLI not found. Installing...", Colors.YELLOW)
        run_command("sudo apt install gh -y" if shutil.which("apt") else "sudo yum install gh -y", tee=True)

    # asciinema
    if not shutil.which("asciinema"):
        log("Asciinema not found. Installing...", Colors.YELLOW)
        run_command("sudo apt install asciinema -y" if shutil.which("apt") else "sudo yum install asciinema -y", tee=True)
    else:
        log("Asciinema detected.", Colors.GREEN)

    # Docker
    if not shutil.which("docker"):
        log("Docker not found. Installing...", Colors.YELLOW)
        run_command("sudo apt install docker.io -y" if shutil.which("apt") else "sudo yum install docker -y", tee=True)
    else:
        log("Docker detected.", Colors.GREEN)

    # PyYAML
    global yaml, PY_YAML
    try:
        import yaml
        PY_YAML = True
        log("PyYAML detected.", Colors.GREEN)
    except ImportError:
        PY_YAML = False
        log("PyYAML not found. Installing...", Colors.YELLOW)
        run_command(f"{sys.executable} -m pip install --upgrade PyYAML", tee=True)
        import yaml
        PY_YAML = True

def load_config():
    if PY_YAML and Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r") as f:
            cfg = yaml.safe_load(f) or {}
        log(f"Loaded config from {CONFIG_FILE}", Colors.GREEN)
        return cfg
    return {}

def save_config(cfg):
    if PY_YAML:
        with open(CONFIG_FILE, "w") as f:
            yaml.safe_dump(cfg, f)
        log(f"Saved config to {CONFIG_FILE}", Colors.GREEN)

def docker_prompt_and_build(cfg, project_path):
    if confirm("Do you want to run this inside Docker for full isolation?"):
        docker_tag = cfg.get("docker_tag", "github_push_assistant")
        log(f"Building Docker image '{docker_tag}'...", Colors.YELLOW)
        dockerfile = Path(project_path) / "Dockerfile"
        if not dockerfile.exists():
            dockerfile.write_text("""
FROM python:3.12-slim
WORKDIR /workspace
RUN pip install --upgrade pip
RUN pip install PyYAML gh asciinema
COPY . /workspace
ENTRYPOINT ["python3", "github_push_assistant.py"]
""")
        run_command(f"docker build -t {docker_tag} {project_path}")
        log(f"Docker image '{docker_tag}' ready. Run with:\n"
            f"docker run -it -v {project_path}:/workspace {docker_tag}", Colors.GREEN)
        cfg["docker_tag"] = docker_tag
        save_config(cfg)

def generate_d3_html(project_path):
    vis_path = Path(project_path) / VIS_DIR
    vis_path.mkdir(exist_ok=True)
    html_file = vis_path / "commits.html"
    cmd = "git log --pretty=format:'{\"hash\":\"%h\",\"author\":\"%an\",\"date\":\"%ad\",\"message\":\"%s\"},' | sed '$ s/,$//'"
    success, log_json, _ = run_command(cmd)
    commits_json = f"[{log_json}]" if success else "[]"
    html_file.write_text(f"""
<!DOCTYPE html>
<meta charset="utf-8">
<title>Git Commit Visualization</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<body>
<h2>Commit History</h2>
<svg width="1000" height="600"></svg>
<script>
const commits = {commits_json};
const svg = d3.select("svg");
const margin = {{top: 20, right: 20, bottom: 30, left: 50}};
const width = +svg.attr("width") - margin.left - margin.right;
const height = +svg.attr("height") - margin.top - margin.bottom;
const g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
const x = d3.scalePoint().domain(d3.range(commits.length)).range([0, width]);
const y = d3.scaleLinear().domain([0, commits.length]).range([height, 0]);
g.selectAll("circle")
    .data(commits)
    .enter().append("circle")
    .attr("cx", (d,i) => x(i))
    .attr("cy", (d,i) => y(i))
    .attr("r", 6)
    .attr("fill", "steelblue")
    .append("title")
    .text(d => d.message + " by " + d.author + " on " + d.date);
</script>
</body>
""")
    log(f"D3.js commit visualization generated at {html_file}", Colors.GREEN)

def asciinema_first_run():
    if confirm("Do you want to record this run with asciinema?"):
        run_command(f"asciinema rec -y {FIRST_RUN_CAST} --command 'python3 github_push_assistant.py'")

def main():
    if Path(LOG_FILE).exists():
        Path(LOG_FILE).unlink()
    log("🔧 GitHub Push Assistant with D3.js & Asciinema", Colors.BOLD)

    check_and_install_dependencies()

    cfg = load_config()
    default_path = cfg.get("project_path", str(Path.cwd()))
    project_path = get_input("Project path", default_path)
    cfg["project_path"] = project_path
    save_config(cfg)
    log(f"Working in: {project_path}", Colors.GREEN)

    docker_prompt_and_build(cfg, project_path)

    os.chdir(project_path)
    if not (Path(project_path) / ".git").exists():
        log("Initializing new git repo...", Colors.YELLOW)
        run_command("git init")
        run_command("git branch -M main")
    else:
        log("Git repo exists.", Colors.GREEN)

    success, gh_status, _ = run_command("gh auth status")
    if "Logged in" not in gh_status:
        log("GitHub CLI not authenticated.", Colors.RED)
        if confirm("Run 'gh auth login' now?"):
            run_command("gh auth login", tee=True)
        else:
            log("Authentication required to push. Exiting.", Colors.RED)
            sys.exit(1)

    default_repo = cfg.get("github_repo_name", Path(project_path).name)
    repo_name = get_input("GitHub repo name", default_repo)
    cfg["github_repo_name"] = repo_name
    save_config(cfg)
    success, _, _ = run_command(f"gh repo create {repo_name} --source=. --public --push")
    if not success:
        log(f"Remote repo may already exist.", Colors.RED)

    log("➕ Staging all files...", Colors.YELLOW)
    run_command("git add .")
    default_msg = cfg.get("commit_message", "Initial commit via github_push_assistant")
    commit_msg = get_input("Commit message", default_msg)
    cfg["commit_message"] = commit_msg
    save_config(cfg)
    run_command(f'git commit -m "{commit_msg}"')
    log("🌐 Pushing changes...", Colors.YELLOW)
    run_command("git push origin main", tee=True)

    # Generate D3.js visualization
    generate_d3_html(project_path)

    # Optionally record with asciinema
    asciinema_first_run()

    log("✅ Workflow complete with D3.js visualization.", Colors.GREEN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Push cancelled by user.", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        log(f"Unexpected error: {e}", Colors.RED)
        sys.exit(1)
