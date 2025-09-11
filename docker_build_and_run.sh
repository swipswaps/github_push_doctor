#!/usr/bin/env bash
# Fully abstracted Docker build + run wrapper

set -euo pipefail
LOGFILE="docker_build_and_run.log"

echo "🐳 Building Docker image 'github_push_assistant'..." | tee -a "$LOGFILE"
if docker build -t github_push_assistant . 2>&1 | tee -a "$LOGFILE"; then
    echo "✅ Docker image built successfully" | tee -a "$LOGFILE"
else
    echo "⚠️ Docker build failed, continuing natively" | tee -a "$LOGFILE"
fi

echo "🚀 Running container..." | tee -a "$LOGFILE"
docker run -it -v "$(pwd)":/workspace github_push_assistant | tee -a "$LOGFILE"
