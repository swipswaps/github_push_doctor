# Dockerfile for GitHub Push Assistant
FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y \
    git \
    curl \
    gh \
    asciinema \
 && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy project files
COPY . /app

# Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Persist configs and logs
VOLUME ["/app/github_push_config.yaml", "/app/github_push_assistant.log"]

# Default command
CMD ["python3","github_push_assistant.py"]
