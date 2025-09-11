#!/usr/bin/env bash
# Record the first run with asciinema and Docker automatically

set -euo pipefail
LOGFILE="github_push_assistant_first_run.log"
CASTFILE="github_push_assistant_first_run.cast"

echo "🎥 Recording first run automatically..." | tee -a "$LOGFILE"
asciinema rec -y --overwrite "$CASTFILE" --command "python3 github_push_assistant.py 2>&1 | tee -a $LOGFILE"
echo "✅ Recording complete: $CASTFILE" | tee -a "$LOGFILE"
