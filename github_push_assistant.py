#!/usr/bin/env python3
"""
github_push_assistant.py - PRF-compliant GitHub Push Assistant
- Full verbatim output of git, gh, and system commands
- Writes readable D3.js commit visualization
- Handles Git user configuration interactively
- Generates cd autofill script
"""

import os
import subprocess
import json
from datetime import datetime

LOG_FILE = "github_push_assistant.log"
VIZ_DIR = "visualization"
VIZ_FILE = os.path.join(VIZ_DIR, "visualization.html")
CD_SCRIPT = "cd_to_repo.sh"

def log(msg):
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

def run_cmd(cmd, capture_output=True):
    """Run system command and log verbatim output"""
    log(f"$ {' '.join(cmd)}")
    try:
        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            out = result.stdout.strip()
            err = result.stderr.strip()
            if out:
                log(out)
            if err:
                log(err)
            return result.returncode, out, err
        else:
            result = subprocess.run(cmd)
            return result.returncode, "", ""
    except Exception as e:
        log(f"ERROR: {e}")
        return 1, "", str(e)

def ensure_git_config():
    """Prompt user for git name/email if missing and set globally"""
    code, name_out, _ = run_cmd(["git", "config", "--global", "user.name"])
    if not name_out.strip():
        name = input("Git user.name not set. Enter your name: ")
        run_cmd(["git", "config", "--global", "user.name", name])
    code, email_out, _ = run_cmd(["git", "config", "--global", "user.email"])
    if not email_out.strip():
        email = input("Git user.email not set. Enter your email: ")
        run_cmd(["git", "config", "--global", "user.email", email])

def generate_cd_script():
    """Generate cd autofill shell script"""
    with open(CD_SCRIPT, "w") as f:
        f.write(f"#!/bin/bash\ncd {os.getcwd()}\n")
    os.chmod(CD_SCRIPT, 0o755)
    log(f"CD autofill script generated: {CD_SCRIPT}")

def get_commits():
    """Collect commits as list of dicts for D3 visualization"""
    code, out, _ = run_cmd(["git", "log", "--pretty=format:{\"hash\":\"%h\", \"message\":\"%s\", \"date\":\"%ad\"}", "--date=short"])
    commits = []
    if out.strip():
        for line in out.splitlines():
            try:
                commits.append(json.loads(line))
            except json.JSONDecodeError:
                log(f"ERROR decoding commit line: {line}")
    return commits[::-1]  # reverse chronological order

def write_visualization(commits):
    """Write multi-row wrapped D3.js visualization into visualization folder"""
    os.makedirs(VIZ_DIR, exist_ok=True)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>D3.js Commit Visualization</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  svg {{ font-family: sans-serif; }}
  circle:hover {{ fill: orange; cursor: pointer; }}
  text {{ font-size: 12px; }}
</style>
</head>
<body>
<h1>Commit History Visualization</h1>
<svg id="chart" width="1200" height="600"></svg>
<script>
const commits = {json.dumps(commits)};
const svg = d3.select("#chart");
const rowLength = 5;
const xSpacing = 200;
const ySpacing = 100;

svg.selectAll("circle")
   .data(commits)
   .enter()
   .append("circle")
   .attr("cx", (d, i) => 50 + (i % rowLength) * xSpacing)
   .attr("cy", (d, i) => 50 + Math.floor(i / rowLength) * ySpacing)
   .attr("r", 20)
   .style("fill", "steelblue")
   .append("title")
   .text(d => d.hash + ": " + d.message);

svg.selectAll("text")
   .data(commits)
   .enter()
   .append("text")
   .attr("x", (d, i) => 50 + (i % rowLength) * xSpacing)
   .attr("y", (d, i) => 50 + Math.floor(i / rowLength) * ySpacing + 40)
   .attr("text-anchor", "middle")
   .text(d => d.message)
   .call(function wrapText(text) {{
       text.each(function() {{
           const t = d3.select(this);
           const words = t.text().split(/\\s+/).reverse();
           let word, line = [];
           const lineHeight = 1.1;
           let y = t.attr("y");
           let tspan = t.text(null).append("tspan").attr("x", t.attr("x")).attr("y", y);
           while(word = words.pop()) {{
               line.push(word);
               tspan.text(line.join(" "));
               if(tspan.node().getComputedTextLength() > 180) {{
                   line.pop();
                   tspan.text(line.join(" "));
                   line = [word];
                   tspan = t.append("tspan").attr("x", t.attr("x")).attr("y", +y + lineHeight*12).text(word);
                   y = +y + lineHeight*12;
               }}
           }}
       }});
   }});
</script>
</body>
</html>
"""
    with open(VIZ_FILE, "w") as f:
        f.write(html_content)
    log(f"✅ Visualization generated: {VIZ_FILE}")

def main():
    log("🔧 Running GitHub Push Assistant with full verbatim output")
    # Detect versions
    run_cmd(["git", "--version"])
    run_cmd(["gh", "--version"])
    run_cmd(["asciinema", "--version"])
    run_cmd(["docker", "--version"])

    project_path = input(f"Project path [{os.getcwd()}]: ").strip() or os.getcwd()
    os.chdir(project_path)
    log(f"Working in: {project_path}")

    # Docker build attempt
    ret, _, _ = run_cmd(["docker", "build", "-t", "github_push_assistant", project_path])
    if ret != 0:
        log("⚠️ Docker build failed, falling back to direct execution")

    # Ensure git config
    ensure_git_config()

    # GitHub auth
    run_cmd(["gh", "auth", "status"])

    # Init git repo
    run_cmd(["git", "init"])
    run_cmd(["git", "add", "."])
    commit_message = input("Commit message [auto]: ").strip() or "auto"
    run_cmd(["git", "commit", "-m", commit_message])

    # Push
    ret, _, _ = run_cmd(["git", "remote", "grep", "origin"])
    if ret != 0:
        log("origin missing")
    run_cmd(["git", "push", "origin", "HEAD"])

    # Generate visualization
    commits = get_commits()
    if commits:
        write_visualization(commits)
    else:
        log("⚠️ No commits found for visualization")

    # Generate cd autofill script
    generate_cd_script()
    log("✅ Workflow complete. Visualization created and push attempted.")

if __name__ == "__main__":
    main()
