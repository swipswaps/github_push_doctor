# /Dockerfile
FROM python:3.12-slim

WORKDIR /workspace

RUN pip install --upgrade pip
RUN pip install PyYAML>=6.0 asciinema>=2.0.0

RUN apt-get update && \
    apt-get install -y curl git unzip && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

COPY . /workspace
EXPOSE 8000
ENTRYPOINT ["python3", "github_push_assistant.py"]
