#!/usr/bin/env bash
# Record first run of GitHub Push Assistant with asciinema + tee logging
# Auto-captures session for auditing or demo

set -euo pipefail
LOGFILE="github_push_assistant_first_run.log"
CASTFILE="github_push_assistant_first_run.cast"

echo "🎥 Recording with asciinema, logging to $LOGFILE..."
asciinema rec -y "$CASTFILE" --command "python3 github_push_assistant.py 2>&1 | tee -a $LOGFILE"
