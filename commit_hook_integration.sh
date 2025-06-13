#!/bin/bash
# Git post-commit hook script to trigger project management updates

# Path to the GravityWaves workspace
WORKSPACE_DIR="/workspaces/GravityWaves"

# Activate Python environment if needed
# source $WORKSPACE_DIR/venv/bin/activate

# Run the task scoring and status update script
python3 $WORKSPACE_DIR/project_task_scoring.py

# Run the report generation script
python3 $WORKSPACE_DIR/project_management_reports.py

echo "Project management data and reports updated after commit."
