# GitHub Push Assistant (Docker-ready)

Automated assistant to push any folder/project to GitHub.
Supports configuration persistence, interactive prompts, and logging.

---

## Features

- Detects git, gh CLI, PyYAML, asciinema
- Saves interactive settings to `github_push_config.yaml`
- Logs all commands and outputs to `github_push_assistant.log`
- Fully Dockerized for reproducible environments

---

## Setup

1. Clone or copy project folder.
2. Ensure Docker installed (optional, recommended).
3. Python dependencies:
   ```bash
   pip install -r requirements.txt
