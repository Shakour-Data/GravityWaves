#!/usr/bin/env python3
import subprocess
import json
import re
from datetime import datetime

COMMITS_FILE = "Docs/Initial_plan/data/automatic_creation/commits.json"

def get_git_commits():
    # Get git log with commit hash, date, author, and message
    git_log_format = "%H%x1f%an%x1f%ad%x1f%s%x1e"
    try:
        result = subprocess.run(
            ["git", "log", f"--pretty=format:{git_log_format}", "--date=iso"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        raw_log = result.stdout.strip("\n\x1e")
        commits = []
        for entry in raw_log.split("\x1e"):
            parts = entry.strip().split("\x1f")
            if len(parts) == 4:
                commit_hash, author, date_str, message = parts
                commits.append({
                    "commit_hash": commit_hash,
                    "author": author,
                    "date": date_str,
                    "message": message,
                    "linked_task_ids": extract_task_ids(message),
                })
        return commits
    except subprocess.CalledProcessError as e:
        print(f"Error running git log: {e.stderr}")
        return []

def extract_task_ids(message):
    # Extract task IDs from commit message using pattern #<id>
    pattern = re.compile(r"#(\\d+)")
    matches = pattern.findall(message)
    return [int(m) for m in matches]

def save_commits(commits):
    with open(COMMITS_FILE, "w", encoding="utf-8") as f:
        json.dump(commits, f, indent=2, ensure_ascii=False)

def main():
    commits = get_git_commits()
    save_commits(commits)
    print(f"Extracted {len(commits)} commits and saved to {COMMITS_FILE}")

if __name__ == "__main__":
    main()
