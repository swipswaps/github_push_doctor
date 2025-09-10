# GitHub Push Assistant

A smooth, beginner-friendly assistant that stages, commits, and pushes your project to GitHub.  
It remembers your preferences between runs using a YAML config file.

---

## 🚀 Features
- Initializes a Git repo if missing
- Saves answers in `github_push_config.yaml` for persistence
- Reloads config and shows defaults on next run
- Optional `--auto` flag for zero-interaction pushes
- Uses [`gh`](https://cli.github.com/) for repo creation and push
- Works in any project folder

---

## 📦 Requirements
- Python 3.8+
- Git
- GitHub CLI (`gh`) – must be authenticated (`gh auth login`)
- PyYAML (`pip install -r requirements.txt`)

---

## 🛠 Installation
```bash
# Clone or copy files into a folder
cd ~/my-tools
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
