#!/usr/bin/env bash
# /record_first_run.sh
# Automatically record first run of github_push_assistant.py with asciinema

LOG_CAST="github_push_assistant_first_run.cast"

if ! command -v asciinema &> /dev/null
then
    echo "Asciinema not installed. Installing..."
    if command -v apt &> /dev/null; then
        sudo apt install -y asciinema
    elif command -v yum &> /dev/null; then
        sudo yum install -y asciinema
    else
        echo "Package manager not found. Install asciinema manually."
        exit 1
    fi
fi

echo "Recording first run of github_push_assistant.py"
asciinema rec -y "$LOG_CAST" --command "python3 github_push_assistant.py"
echo "Recording saved to $LOG_CAST"
