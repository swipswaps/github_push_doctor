# GitHub Push Assistant

A guided, interactive Python script to push any local project folder to GitHub.  
Supports automatic repo creation, `gh` CLI integration, commit/branch management, and persistent YAML config.

---

## Features

- Detects Git installation and configuration
- Validates GitHub authentication via `gh`
- Guides user through project folder selection
- Stages, commits, and pushes changes automatically
- Creates GitHub repository if it doesn't exist
- Saves all user choices in `github_push_config.yaml`
- Re-loads config for future runs
- Color-coded terminal output and smooth step-by-step UX

---

## Requirements

- Python 3.7+
- Git
- GitHub CLI (`gh`)
- PyYAML (`pip install pyyaml`)

---

## Usage

1. Navigate to your project folder:
   ```bash
   cd /path/to/project
