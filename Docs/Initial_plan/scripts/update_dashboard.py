#!/usr/bin/env python3
import json
from datetime import datetime

TASKS_FILE = "Docs/Initial_plan/tasks.json"
COMMITS_FILE = "Docs/Initial_plan/commits.json"
IMPORTANCE_LEVELS_FILE = "Docs/Initial_plan/importance_levels.json"
URGENCY_LEVELS_FILE = "Docs/Initial_plan/urgency_levels.json"
TASK_ASSIGNMENTS_FILE = "Docs/Initial_plan/task_assignments.json"
RESOURCES_FILE = "Docs/Initial_plan/resources.json"
DASHBOARD_FILE = "Docs/Initial_plan/Project_Dashboard.txt"

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_level_description(levels, value):
    for level in levels:
        if level["level"] == value:
            return level["description"]
    return "Unknown"

def summarize_tasks(tasks, importance_levels, urgency_levels):
    total_tasks = len(tasks)
    completed_tasks = [t for t in tasks if t["status"].lower() == "done"]
    completed_count = len(completed_tasks)
    progress_percent = (completed_count / total_tasks) * 100 if total_tasks > 0 else 0

    important_tasks = [t for t in tasks if t["importance"] >= 4]
    urgent_tasks = [t for t in tasks if t["urgency"] >= 4]

    # Sort important and urgent tasks by importance and urgency descending
    important_tasks_sorted = sorted(important_tasks, key=lambda x: x["importance"], reverse=True)
    urgent_tasks_sorted = sorted(urgent_tasks, key=lambda x: x["urgency"], reverse=True)

    return {
        "total_tasks": total_tasks,
        "completed_count": completed_count,
        "progress_percent": progress_percent,
        "completed_tasks": completed_tasks,
        "important_tasks": important_tasks_sorted,
        "urgent_tasks": urgent_tasks_sorted,
    }

def format_task(task, importance_levels, urgency_levels):
    importance_desc = get_level_description(importance_levels, task["importance"])
    urgency_desc = get_level_description(urgency_levels, task["urgency"])
    assigned_to = task.get("assigned_to", "Unassigned")
    return f'- [{task["id"]}] {task["name"]} (Status: {task["status"]}, Importance: {importance_desc}, Urgency: {urgency_desc}, Assigned to: {assigned_to})'

def main():
    tasks = load_json_file(TASKS_FILE)
    commits = load_json_file(COMMITS_FILE)
    importance_levels = load_json_file(IMPORTANCE_LEVELS_FILE)
    urgency_levels = load_json_file(URGENCY_LEVELS_FILE)
    task_assignments = load_json_file(TASK_ASSIGNMENTS_FILE)
    resources = load_json_file(RESOURCES_FILE)

    # Map resource id to name
    resource_map = {r["id"]: r["name"] for r in resources if r["type"] == "human"}

    # Add assigned_to field to tasks based on task_assignments
    for task in tasks:
        assigned_resource_id = task_assignments.get(str(task["id"])) or task_assignments.get(task["id"])
        if assigned_resource_id is not None:
            task["assigned_to"] = resource_map.get(assigned_resource_id, "Unassigned")
        else:
            task["assigned_to"] = "Unassigned"

    summary = summarize_tasks(tasks, importance_levels, urgency_levels)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append(f"Project Dashboard - Updated: {now_str}")
    lines.append("=" * 50)
    lines.append(f"Total Tasks: {summary['total_tasks']}")
    lines.append(f"Completed Tasks: {summary['completed_count']}")
    lines.append(f"Overall Progress: {summary['progress_percent']:.2f}%")
    lines.append("")

    lines.append("Completed Tasks:")
    if summary["completed_tasks"]:
        for task in summary["completed_tasks"]:
            lines.append(format_task(task, importance_levels, urgency_levels))
    else:
        lines.append("  None")
    lines.append("")

    lines.append("Important Tasks (Importance >= High):")
    if summary["important_tasks"]:
        for task in summary["important_tasks"]:
            lines.append(format_task(task, importance_levels, urgency_levels))
    else:
        lines.append("  None")
    lines.append("")

    lines.append("Urgent Tasks (Urgency >= High):")
    if summary["urgent_tasks"]:
        for task in summary["urgent_tasks"]:
            lines.append(format_task(task, importance_levels, urgency_levels))
    else:
        lines.append("  None")
    lines.append("")

    lines.append("Task Assignments:")
    for task in tasks:
        lines.append(f'  - [{task["id"]}] {task["name"]}: {task["assigned_to"]}')
    lines.append("")

    dashboard_content = "\\n".join(lines)

    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(dashboard_content)

    print(f"Dashboard updated and saved to {DASHBOARD_FILE}")

if __name__ == "__main__":
    main()
