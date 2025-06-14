import json
from datetime import datetime, timedelta

TASKS_FILE = "tasks.json"
RESOURCES_FILE = "resources.json"
SCORES_FILE = "task_scores.json"
REPORTS_DIR = "reports/"

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_report(filename, content):
    import os
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    with open(REPORTS_DIR + filename, "w", encoding="utf-8") as f:
        f.write(content)

def daily_task_status_report():
    tasks = load_json(TASKS_FILE)
    scores = load_json(SCORES_FILE)
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    # Map scores by task_id
    score_map = {s["task_id"]: s for s in scores}

    report_lines = []
    report_lines.append(f"Daily Task Status Report - {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append("Task ID | Name | Status | Importance | Urgency | Overall | Status Changed\n")
    report_lines.append("-" * 80)

    for task in tasks:
        task_id = task["id"]
        score = score_map.get(task_id, {})
        status = score.get("status", "Unknown")
        importance = score.get("importance", "N/A")
        urgency = score.get("urgency", "N/A")
        overall = score.get("overall", "N/A")
        # For demo, assume status changed if task has commits today (not implemented here)
        status_changed = "Yes" if False else "No"
        report_lines.append(f"{task_id} | {task['name']} | {status} | {importance} | {urgency} | {overall} | {status_changed}")

    save_report(f"daily_task_status_{now.strftime('%Y%m%d')}.txt", "\n".join(report_lines))

def resource_utilization_report():
    tasks = load_json(TASKS_FILE)
    resources = load_json(RESOURCES_FILE)

    resource_hours = {r["id"]: 0 for r in resources}
    resource_names = {r["id"]: r["name"] for r in resources}

    for task in tasks:
        assigned = task.get("assigned_resources", [])
        duration = task.get("duration_days", 1)
        for res_id in assigned:
            resource_hours[res_id] += duration * 8  # Assume 8 hours per day

    report_lines = []
    report_lines.append("Resource Utilization Report\n")
    report_lines.append("Resource ID | Name | Estimated Hours\n")
    report_lines.append("-" * 50)
    for res_id, hours in resource_hours.items():
        report_lines.append(f"{res_id} | {resource_names.get(res_id, 'Unknown')} | {hours}")

    save_report(f"resource_utilization_{datetime.now().strftime('%Y%m%d')}.txt", "\n".join(report_lines))

def sprint_progress_report():
    # Placeholder for sprint data
    report_lines = []
    report_lines.append("Sprint Progress Report\n")
    report_lines.append("Sprint goals, completed tasks, remaining tasks, velocity, burndown data.\n")
    report_lines.append("This report needs sprint data integration.\n")

    save_report(f"sprint_progress_{datetime.now().strftime('%Y%m%d')}.txt", "\n".join(report_lines))

def risk_and_issue_report():
    tasks = load_json(TASKS_FILE)
    report_lines = []
    report_lines.append("Risk and Issue Report\n")
    report_lines.append("Tasks with high risk scores and open issues.\n")
    report_lines.append("-" * 50)
    for task in tasks:
        risk = task.get("risk", 0)
        if risk > 70:
            report_lines.append(f"Task ID: {task['id']}, Name: {task['name']}, Risk: {risk}")

    save_report(f"risk_and_issue_{datetime.now().strftime('%Y%m%d')}.txt", "\n".join(report_lines))

def ai_assisted_summary_report():
    tasks = load_json(TASKS_FILE)
    scores = load_json(SCORES_FILE)
    now = datetime.now()

    urgent_tasks = [s for s in scores if s.get("urgency", 0) >= 70]
    important_tasks = [s for s in scores if s.get("importance", 0) >= 70]

    report_lines = []
    report_lines.append(f"AI-Assisted Summary Report - {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append(f"Total Tasks: {len(tasks)}")
    report_lines.append(f"Urgent Tasks (Urgency >= 70): {len(urgent_tasks)}")
    report_lines.append(f"Important Tasks (Importance >= 70): {len(important_tasks)}\n")

    report_lines.append("Top 5 Urgent Tasks:")
    for task in sorted(urgent_tasks, key=lambda x: x["urgency"], reverse=True)[:5]:
        report_lines.append(f"- {task['name']} (Urgency: {task['urgency']})")

    report_lines.append("\nTop 5 Important Tasks:")
    for task in sorted(important_tasks, key=lambda x: x["importance"], reverse=True)[:5]:
        report_lines.append(f"- {task['name']} (Importance: {task['importance']})")

    report_lines.append("\nRecommended Next Actions:")
    next_actions = sorted(scores, key=lambda x: x["overall"], reverse=True)[:5]
    for task in next_actions:
        report_lines.append(f"- {task['name']} (Overall Score: {task['overall']})")

    save_report(f"ai_summary_{now.strftime('%Y%m%d')}.txt", "\n".join(report_lines))

if __name__ == "__main__":
    daily_task_status_report()
    resource_utilization_report()
    sprint_progress_report()
    risk_and_issue_report()
    ai_assisted_summary_report()
