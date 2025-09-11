# GitHub Push Assistant Dockerfile
FROM python:3.11-slim

# Install deps
RUN apt-get update && apt-get install -y git gh docker.io asciinema && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "github_push_assistant.py"]
