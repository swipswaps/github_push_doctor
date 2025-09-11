#!/usr/bin/env python3
"""
GitHub GraphQL collector for repo data
"""
import os
import json
from pathlib import Path
from subprocess import run, PIPE

DATA_FILE = "github_repo_data.json"

def run_gh_graphql(query):
    import subprocess
    import json
    cmd = f'gh api graphql -f query="{query}"'
    result = subprocess.run(cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True)
    if result.returncode != 0:
        print("GraphQL query failed:", result.stderr)
        return None
    return json.loads(result.stdout)

def collect_repo_data(repo_name):
    owner = os.getenv("GH_OWNER") or "swipswaps"
    query = f"""
    {{
      repository(owner: "{owner}", name: "{repo_name}") {{
        name
        defaultBranchRef {{ name }}
        refs(first: 50, refPrefix:"refs/heads/") {{ nodes {{ name }} }}
        pullRequests(last:50) {{ nodes {{ title, createdAt, mergedAt, author{{login}} }} }}
        issues(last:50) {{ nodes {{ title, createdAt, closedAt, state }} }}
        object(expression:"main") {{
          ... on Commit {{
            history(first:50) {{
              nodes {{ message, committedDate, author{{name,email}} }}
            }}
          }}
        }}
      }}
    }}
    """
    data = run_gh_graphql(query)
    if data:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Repository data saved to {DATA_FILE}")
