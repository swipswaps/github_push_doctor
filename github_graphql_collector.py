#!/usr/bin/env python3
"""
GitHub GraphQL Collector
Fetches metadata (repos, commits) from GitHub using gh CLI GraphQL API.
"""

import subprocess
import json
from pathlib import Path


def run_query(query: str) -> dict:
    """Run GraphQL query with gh CLI"""
    cmd = f"gh api graphql -f query='{query}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return json.loads(result.stdout)


def main():
    query = """
    {
      viewer {
        login
        repositories(first: 5, orderBy: {field: UPDATED_AT, direction: DESC}) {
          nodes {
            name
            url
          }
        }
      }
    }
    """
    data = run_query(query)
    Path("graphql_output.json").write_text(json.dumps(data, indent=2))
    print("✅ Saved graphql_output.json")


if __name__ == "__main__":
    main()
