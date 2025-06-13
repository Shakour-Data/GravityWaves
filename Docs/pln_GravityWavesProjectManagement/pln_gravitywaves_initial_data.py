import json
from datetime import date, timedelta
from pln_app import db, Task, Resource, WorkCycleStage

def seed_initial_data():
    # Seed resources
    resources = [
        Resource(name="Data Analyst", hourly_rate=45.0, type="human"),
        Resource(name="Data Scientist", hourly_rate=60.0, type="human"),
        Resource(name="Quantitative Analyst", hourly_rate=65.0, type="human"),
        Resource(name="Software Engineer", hourly_rate=55.0, type="human"),
        Resource(name="Financial Budget", hourly_rate=0.0, type="financial"),
    ]
    for res in resources:
        existing = Resource.query.filter_by(name=res.name).first()
        if not existing:
            db.session.add(res)
    db.session.commit()

    # Seed Agile work cycle stages if not present
    if WorkCycleStage.query.count() == 0:
        default_stages = [
            {"name": "Backlog", "description": "Task is in backlog", "order": 1},
            {"name": "To Do", "description": "Task ready to start", "order": 2},
            {"name": "In Progress", "description": "Task is being worked on", "order": 3},
            {"name": "Code Review", "description": "Task is under code review", "order": 4},
            {"name": "Documentation - In Code", "description": "Writing documentation inside the code", "order": 5},
            {"name": "Documentation - External", "description": "Writing external documentation", "order": 6},
            {"name": "Testing", "description": "Task is being tested", "order": 7},
            {"name": "Done", "description": "Task is completed", "order": 8},
        ]
        for stage in default_stages:
            db.session.add(WorkCycleStage(**stage))
        db.session.commit()

    # Seed importance levels from JSON file
    with open("Docs/pln_GravityWavesProjectManagement/pln_data_json/importance_levels.json", "r", encoding="utf-8") as f:
        importance_levels_data = json.load(f)

    for level_data in importance_levels_data:
        existing = db.session.execute(
            "SELECT 1 FROM importance_levels WHERE level = :level", {"level": level_data["level"]}
        ).fetchone()
        if not existing:
            db.session.execute(
                "INSERT INTO importance_levels (level, description) VALUES (:level, :description)",
                {"level": level_data["level"], "description": level_data["description"]},
            )
    db.session.commit()

    # Seed urgency levels from JSON file
    with open("Docs/pln_GravityWavesProjectManagement/pln_data_json/urgency_levels.json", "r", encoding="utf-8") as f:
        urgency_levels_data = json.load(f)

    for level_data in urgency_levels_data:
        existing = db.session.execute(
            "SELECT 1 FROM urgency_levels WHERE level = :level", {"level": level_data["level"]}
        ).fetchone()
        if not existing:
            db.session.execute(
                "INSERT INTO urgency_levels (level, description) VALUES (:level, :description)",
                {"level": level_data["level"], "description": level_data["description"]},
            )

if __name__ == "__main__":
    from pln_app import app
    with app.app_context():
        seed_initial_data()
