import json
import os
from datetime import datetime, timedelta
import re

# File paths
TASKS_FILE = "tasks.json"
SCORES_FILE = "task_scores.json"
COMMITS_FILE = "commits.json"

# Load tasks from JSON file
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Load commits from JSON file
def load_commits():
    if not os.path.exists(COMMITS_FILE):
        return []
    with open(COMMITS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Save scores to JSON file
def save_scores(scores):
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)

# Build task hierarchy map: task_id -> list of child task_ids
def build_task_hierarchy(tasks):
    hierarchy = {}
    for task in tasks:
        parent_id = task.get("parent_id")
        if parent_id:
            hierarchy.setdefault(parent_id, []).append(task["id"])
    return hierarchy

# Recursive function to aggregate scores from child tasks
def aggregate_scores(task_id, scores_map, hierarchy):
    if task_id not in hierarchy:
        return scores_map.get(task_id, {"importance": 0, "urgency": 0, "overall": 0})
    child_scores = [aggregate_scores(child_id, scores_map, hierarchy) for child_id in hierarchy[task_id]]
    agg_importance = sum(s["importance"] for s in child_scores) / len(child_scores) if child_scores else 0
    agg_urgency = sum(s["urgency"] for s in child_scores) / len(child_scores) if child_scores else 0
    agg_overall = sum(s["overall"] for s in child_scores) / len(child_scores) if child_scores else 0
    return {
        "importance": round(agg_importance),
        "urgency": round(agg_urgency),
        "overall": round(agg_overall),
    }

# Calculate importance score (1-100)
def calculate_importance(task):
    weights = {
        "business_value": 0.35,
        "complexity": 0.25,
        "stakeholder_priority": 0.2,
        "risk": 0.1,
        "dependencies": 0.1,
    }
    score = (
        task.get("business_value", 50) * weights["business_value"] +
        task.get("complexity", 50) * weights["complexity"] +
        task.get("stakeholder_priority", 50) * weights["stakeholder_priority"] +
        (100 - task.get("risk", 50)) * weights["risk"] +
        (100 - task.get("dependencies", 50)) * weights["dependencies"]
    )
    return round(score)

# Calculate urgency score (1-100)
def calculate_urgency(task):
    weights = {
        "deadline_proximity": 0.5,
        "delay_impact": 0.3,
        "external_factors": 0.2,
    }
    deadline_str = task.get("planned_end_date") or task.get("deadline")
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            days_left = (deadline - datetime.now()).days
            deadline_score = max(0, min(100, 100 - days_left))
        except Exception:
            deadline_score = 50
    else:
        deadline_score = 50

    delay_impact = task.get("delay_impact", 50)
    external_factors = task.get("external_factors", 50)

    score = (
        deadline_score * weights["deadline_proximity"] +
        delay_impact * weights["delay_impact"] +
        external_factors * weights["external_factors"]
    )
    return round(score)

# Calculate overall score with weights
def calculate_overall(importance, urgency, w_importance=0.6, w_urgency=0.4):
    return round(w_importance * importance + w_urgency * urgency)

# Link commits to tasks by heuristic analysis of commit messages
def link_commits_to_tasks(tasks, commits):
    task_commit_map = {task["id"]: [] for task in tasks}
    for commit in commits:
        message = commit.get("message", "").lower()
        linked = False
        # Try to match task id by #id pattern
        task_id_pattern = re.compile(r"#(\d+)")
        matches = task_id_pattern.findall(message)
        for match in matches:
            task_id = int(match)
            if task_id in task_commit_map:
                task_commit_map[task_id].append(commit)
                linked = True
        if linked:
            continue
        # If no explicit id, try keyword matching with task names
        for task in tasks:
            task_name = task.get("name", "").lower()
            task_words = set(task_name.split())
            message_words = set(message.split())
            if task_words.intersection(message_words):
                task_commit_map[task["id"]].append(commit)
                linked = True
    return task_commit_map

# Determine task status based on linked commits
def determine_task_status(commits):
    if not commits:
        return "To Do"
    done_keywords = ["done", "complete", "finished", "closed", "resolved"]
    for commit in commits:
        message = commit.get("message", "").lower()
        if any(keyword in message for keyword in done_keywords):
            return "Done"
    return "In Progress"

# Update scores and statuses for all tasks
def update_task_scores_and_statuses():
    tasks = load_tasks()
    commits = load_commits()
    task_commit_map = link_commits_to_tasks(tasks, commits)
    scores = []
    hierarchy = build_task_hierarchy(tasks)
    scores_map = {}

    # Calculate scores for leaf tasks
    for task in tasks:
        importance = calculate_importance(task)
        urgency = calculate_urgency(task)
        overall = calculate_overall(importance, urgency)
        linked_commits = task_commit_map.get(task["id"], [])
        status = determine_task_status(linked_commits)
        score_entry = {
            "task_id": task.get("id"),
            "importance": importance,
            "urgency": urgency,
            "overall": overall,
            "status": status,
            "name": task.get("name"),
            "linked_commits": [c.get("commit_hash") for c in linked_commits],
        }
        scores.append(score_entry)
        scores_map[task["id"]] = score_entry

    # Aggregate scores for parent tasks
    for task in tasks:
        if "parent_id" in task and task["parent_id"]:
            agg_scores = aggregate_scores(task["parent_id"], scores_map, hierarchy)
            scores_map[task["parent_id"]] = {
                "task_id": task["parent_id"],
                "importance": agg_scores["importance"],
                "urgency": agg_scores["urgency"],
                "overall": agg_scores["overall"],
                "status": scores_map.get(task["parent_id"], {}).get("status", "To Do"),
                "name": scores_map.get(task["parent_id"], {}).get("name", ""),
                "linked_commits": scores_map.get(task["parent_id"], {}).get("linked_commits", []),
            }

    # Convert scores_map to list for saving
    final_scores = list(scores_map.values())
    save_scores(final_scores)
    print(f"Updated scores and statuses for {len(final_scores)} tasks.")

# Example usage
if __name__ == "__main__":
    update_task_scores_and_statuses()
