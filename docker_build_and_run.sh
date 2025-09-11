#!/usr/bin/env bash
# Wrapper to build & run the assistant inside Docker
# Handles consistent environment, volume mapping, logging

set -euo pipefail
LOGFILE="docker_build_and_run.log"

echo "🐳 Building Docker image 'github_push_assistant'..." | tee -a "$LOGFILE"
docker build -t github_push_assistant . 2>&1 | tee -a "$LOGFILE"

echo "🚀 Running container..." | tee -a "$LOGFILE"
docker run -it -v "$(pwd)":/workspace github_push_assistant | tee -a "$LOGFILE"
