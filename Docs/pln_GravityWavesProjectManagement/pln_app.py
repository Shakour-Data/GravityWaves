from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), "pln_templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "pln_static"))

# Resource hourly rates in USD
RESOURCE_RATES = {
    "Data Analyst": 41,
    "Data Architect": 57,
    "Software Engineer (10 yrs exp)": 58,
    "Python Developer (3 yrs exp)": 60,
    "Machine Learning Engineer (5 yrs exp)": 63,
    "Frontend Developer (5 yrs exp)": 44,
    "Technical Writer (3 yrs exp)": 39,
    "Technical Writer (1 yr exp)": 32,
    "Technical Analysis Expert": 41,
    "Project Manager (3 yrs exp)": 67,
}

# Task status options
STATUS_OPTIONS = ["To Do", "In Progress", "Done"]

# In-memory storage for tasks and resources (for demo purposes)
tasks = []
resources = []

# Task model example
class Task:
    def __init__(self, id, name, duration_days, planned_start, planned_end,
                 actual_start=None, actual_end=None, status="To Do", assigned_resources=None):
        self.id = id
        self.name = name
        self.duration_days = duration_days
        self.planned_start = planned_start
        self.planned_end = planned_end
        self.actual_start = actual_start
        self.actual_end = actual_end
        self.status = status
        self.assigned_resources = assigned_resources or []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "duration_days": self.duration_days,
            "planned_start": self.planned_start.strftime("%Y-%m-%d"),
            "planned_end": self.planned_end.strftime("%Y-%m-%d"),
            "actual_start": self.actual_start.strftime("%Y-%m-%d") if self.actual_start else "",
            "actual_end": self.actual_end.strftime("%Y-%m-%d") if self.actual_end else "",
            "status": self.status,
            "assigned_resources": self.assigned_resources,
        }

# Resource model example
class Resource:
    def __init__(self, id, name, hourly_rate):
        self.id = id
        self.name = name
        self.hourly_rate = hourly_rate

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "hourly_rate": self.hourly_rate,
        }

@app.route("/")
def index():
    return render_template("pln_index.html")

@app.route("/api/tasks", methods=["GET", "POST"])
def api_tasks():
    if request.method == "GET":
        return jsonify([task.to_dict() for task in tasks])
    elif request.method == "POST":
        data = request.json
        try:
            id = len(tasks) + 1
            name = data["name"]
            duration_days = int(data["duration_days"])
            planned_start = datetime.strptime(data["planned_start"], "%Y-%m-%d")
            planned_end = datetime.strptime(data["planned_end"], "%Y-%m-%d")
            actual_start = datetime.strptime(data["actual_start"], "%Y-%m-%d") if data.get("actual_start") else None
            actual_end = datetime.strptime(data["actual_end"], "%Y-%m-%d") if data.get("actual_end") else None
            status = data.get("status", "To Do")
            assigned_resources = data.get("assigned_resources", [])
            task = Task(id, name, duration_days, planned_start, planned_end,
                        actual_start, actual_end, status, assigned_resources)
            tasks.append(task)
            return jsonify({"message": "Task added", "task": task.to_dict()}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

@app.route("/api/resources", methods=["GET"])
def api_resources():
    # Return predefined resources with rates
    res_list = []
    for i, (name, rate) in enumerate(RESOURCE_RATES.items(), start=1):
        res_list.append({"id": i, "name": name, "hourly_rate": rate})
    return jsonify(res_list)

if __name__ == "__main__":
    # Use port 6060 instead of 6000 to avoid ERR_UNSAFE_PORT in browsers
    app.run(host="0.0.0.0", port=6060, debug=True)
