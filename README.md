# GitHub Push Assistant (Complete Repo)

**Purpose**  
A fully automated assistant that interactively helps you initialize, commit, create a GitHub repo, push your project, optionally run inside Docker, record the session with `asciinema`, and generate a D3.js commit visualization. The assistant manages dependencies, folders, permissions (where possible), YAML config persistence, and comprehensive tee-style logging.

---

## What you get (files emitted in this repo)

- `/github_push_assistant.py` — main interactive assistant (automates dependencies, Docker, GitHub repo creation/push, D3 visualization, asciinema recording)
- `/record_first_run.sh` — wrapper to record a full first run with asciinema and tee logging
- `/docker_build_and_run.sh` — convenient Docker build & run wrapper
- `/Dockerfile` — image for isolation if you choose to use Docker
- `/requirements.txt` — runtime Python deps
- `/requirements-dev.txt` — dev/test tools (pytest, flake8)
- `/tests/test_syntax_and_files.py` — basic tests (syntax / file presence)
- `/.github/workflows/ci.yml` — CI to run lint/tests on push/PR
- `/.gitignore` — common ignores

---

## Quickstart — single-command first-run (recommended)

Open a terminal in the project root and run (this will run the assistant, prompt you for minimal choices, and do the rest):

```bash
# Option A: direct Python run (recommended)
python3 github_push_assistant.py

# Option B: record the first run (recommended for auditing / demos)
./record_first_run.sh

# Option C: build & run in Docker (script can handle from inside)
./docker_build_and_run.sh
