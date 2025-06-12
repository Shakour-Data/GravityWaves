from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), "pln_templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "pln_static"))

# Configuration
DATABASE_URL = os.getenv("PLN_DATABASE_URL", "sqlite:///pln_project_management.db")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models

class WorkCycleStage(db.Model):
    __tablename__ = 'work_cycle_stages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "order": self.order,
        }

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False, default="human")  # human or financial

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "hourly_rate": self.hourly_rate,
            "type": self.type,
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    planned_start = db.Column(db.Date, nullable=False)
    planned_end = db.Column(db.Date, nullable=False)
    actual_start = db.Column(db.Date, nullable=True)
    actual_end = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="To Do")
    importance = db.Column(db.Integer, nullable=False, default=1)  # 1-10 scale
    urgency = db.Column(db.Integer, nullable=False, default=1)     # 1-10 scale
    score = db.Column(db.Float, nullable=False, default=0.0)
    current_stage_id = db.Column(db.Integer, db.ForeignKey('work_cycle_stages.id'), nullable=True)
    current_stage = db.relationship('WorkCycleStage')
    assigned_resources = db.relationship('Resource', secondary='task_resources', backref='tasks')

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
            "importance": self.importance,
            "urgency": self.urgency,
            "score": self.score,
            "current_stage": self.current_stage.to_dict() if self.current_stage else None,
            "assigned_resources": [r.to_dict() for r in self.assigned_resources],
        }

task_resources = db.Table('task_resources',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('resource_id', db.Integer, db.ForeignKey('resources.id'), primary_key=True)
)

class Commit(db.Model):
    __tablename__ = 'commits'
    id = db.Column(db.Integer, primary_key=True)
    commit_hash = db.Column(db.String(40), nullable=False, unique=True)
    message = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    task = db.relationship('Task', backref='commits')

    def to_dict(self):
        return {
            "id": self.id,
            "commit_hash": self.commit_hash,
            "message": self.message,
            "author": self.author,
            "date": self.date.isoformat(),
            "task_id": self.task_id,
        }

# Utility functions

def calculate_task_score(importance, urgency):
    # Simple weighted scoring: weight importance and urgency equally
    return (importance + urgency) / 2.0

def update_task_scores():
    tasks = Task.query.all()
    for task in tasks:
        task.score = calculate_task_score(task.importance, task.urgency)
    db.session.commit()

def update_task_status_from_commits(task):
    # Example logic: if task has commits, mark In Progress or Done based on commits count or message
    if not task.commits:
        task.status = "To Do"
    else:
        # If any commit message contains "done" or "complete", mark Done
        done_keywords = ["done", "complete", "finished", "closed"]
        if any(any(k in c.message.lower() for k in done_keywords) for c in task.commits):
            task.status = "Done"
        else:
            task.status = "In Progress"
    db.session.commit()

def update_all_task_statuses():
    tasks = Task.query.all()
    for task in tasks:
        update_task_status_from_commits(task)

# Routes

@app.route("/")
def index():
    return render_template("pln_index.html")

@app.route("/tasks")
def tasks_page():
    return render_template("tasks.html")

@app.route("/resources")
def resources_page():
    return render_template("resources.html")

@app.route("/gantt")
def gantt_page():
    return render_template("gantt.html")

@app.route("/costs")
def costs_page():
    return render_template("costs.html")

@app.route("/reports")
def reports_page():
    return render_template("reports.html")

@app.route("/api/tasks", methods=["GET", "POST"])
def api_tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        return jsonify([task.to_dict() for task in tasks])
    elif request.method == "POST":
        data = request.json
        try:
            name = data["name"]
            duration_days = int(data["duration_days"])
            planned_start = datetime.strptime(data["planned_start"], "%Y-%m-%d").date()
            planned_end = datetime.strptime(data["planned_end"], "%Y-%m-%d").date()
            actual_start = datetime.strptime(data["actual_start"], "%Y-%m-%d").date() if data.get("actual_start") else None
            actual_end = datetime.strptime(data["actual_end"], "%Y-%m-%d").date() if data.get("actual_end") else None
            status = data.get("status", "To Do")
            importance = int(data.get("importance", 1))
            urgency = int(data.get("urgency", 1))
            current_stage_id = data.get("current_stage_id")
            assigned_resource_ids = data.get("assigned_resource_ids", [])

            task = Task(
                name=name,
                duration_days=duration_days,
                planned_start=planned_start,
                planned_end=planned_end,
                actual_start=actual_start,
                actual_end=actual_end,
                status=status,
                importance=importance,
                urgency=urgency,
                current_stage_id=current_stage_id
            )
            for res_id in assigned_resource_ids:
                resource = Resource.query.get(res_id)
                if resource:
                    task.assigned_resources.append(resource)

            task.score = calculate_task_score(importance, urgency)
            db.session.add(task)
            db.session.commit()
            return jsonify({"message": "Task added", "task": task.to_dict()}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

@app.route("/api/resources", methods=["GET", "POST"])
def api_resources():
    if request.method == "GET":
        resources = Resource.query.all()
        return jsonify([res.to_dict() for res in resources])
    elif request.method == "POST":
        data = request.json
        try:
            name = data["name"]
            hourly_rate = float(data["hourly_rate"])
            type_ = data.get("type", "human")
            resource = Resource(name=name, hourly_rate=hourly_rate, type=type_)
            db.session.add(resource)
            db.session.commit()
            return jsonify({"message": "Resource added", "resource": resource.to_dict()}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

@app.route("/api/work_cycle_stages", methods=["GET"])
def api_work_cycle_stages():
    stages = WorkCycleStage.query.order_by(WorkCycleStage.order).all()
    return jsonify([stage.to_dict() for stage in stages])

@app.route("/api/commits", methods=["GET"])
def api_commits():
    commits = Commit.query.order_by(Commit.date.desc()).all()
    return jsonify([commit.to_dict() for commit in commits])

@app.route("/api/import_commits", methods=["POST"])
def api_import_commits():
    """
    Expects JSON array of commits with fields:
    - commit_hash
    - message
    - author
    - date (ISO format)
    - task_id
    """
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of commits"}), 400
    imported = 0
    for item in data:
        try:
            commit_hash = item["commit_hash"]
            if Commit.query.filter_by(commit_hash=commit_hash).first():
                continue  # skip duplicates
            message = item["message"]
            author = item.get("author")
            date = datetime.fromisoformat(item["date"])
            task_id = item["task_id"]
            task = Task.query.get(task_id)
            if not task:
                continue  # skip commits with invalid task
            commit = Commit(commit_hash=commit_hash, message=message, author=author, date=date, task=task)
            db.session.add(commit)
            imported += 1
        except Exception:
            continue
    db.session.commit()
    update_all_task_statuses()
    update_task_scores()
    return jsonify({"message": f"Imported {imported} commits"}), 201

@app.route("/api/reports/ai_summary", methods=["GET"])
def api_ai_summary_report():
    """
    Generates a structured report suitable for AI consumption summarizing:
    - Project progress by Agile stages
    - Urgent and important tasks
    - Next recommended activities
    """
    tasks = Task.query.all()
    stages = WorkCycleStage.query.order_by(WorkCycleStage.order).all()

    stage_summary = []
    for stage in stages:
        stage_tasks = [t for t in tasks if t.current_stage_id == stage.id]
        stage_summary.append({
            "stage": stage.name,
            "task_count": len(stage_tasks),
            "tasks": [t.to_dict() for t in stage_tasks]
        })

    urgent_tasks = [t.to_dict() for t in tasks if t.urgency >= 7]
    important_tasks = [t.to_dict() for t in tasks if t.importance >= 7]

    next_activities = sorted(tasks, key=lambda t: (-t.score, t.planned_start))[:5]
    report = {
        "stage_summary": stage_summary,
        "urgent_tasks": urgent_tasks,
        "important_tasks": important_tasks,
        "next_recommended_activities": [t.to_dict() for t in next_activities]
    }
    return jsonify(report)

if __name__ == "__main__":
    # Seed default Agile work cycle stages if not present
    with app.app_context():
        if WorkCycleStage.query.count() == 0:
            default_stages = [
                {"name": "Backlog", "description": "Task is in backlog", "order": 1},
                {"name": "To Do", "description": "Task ready to start", "order": 2},
                {"name": "In Progress", "description": "Task is being worked on", "order": 3},
                {"name": "Code Review", "description": "Task is under code review", "order": 4},
                {"name": "Testing", "description": "Task is being tested", "order": 5},
                {"name": "Done", "description": "Task is completed", "order": 6},
            ]
            for stage in default_stages:
                db.session.add(WorkCycleStage(**stage))
            db.session.commit()

    app.run(host="0.0.0.0", port=6060, debug=True)
