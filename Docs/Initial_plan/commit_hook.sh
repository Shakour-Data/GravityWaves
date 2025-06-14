#!/bin/bash
# Commit hook script to update commits.json and project dashboard after each commit

# Run git_commit_extractor.py to update commits.json
python3 Docs/Initial_plan/git_commit_extractor.py

# Run update_dashboard.py to update the dashboard text file
python3 Docs/Initial_plan/update_dashboard.py
