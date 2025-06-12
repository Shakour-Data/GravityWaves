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

    # Seed detailed tasks for GravityWaves project (stock market analysis)
    backlog_stage = WorkCycleStage.query.filter_by(name="Backlog").first()
    today = date.today()
    tasks = [
        Task(
            name="Project Initialization and Planning",
            duration_days=7,
            planned_start=today,
            planned_end=today + timedelta(days=7),
            status="To Do",
            importance=10,
            urgency=9,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
        Task(
            name="Requirement Gathering and Analysis",
            duration_days=10,
            planned_start=today + timedelta(days=8),
            planned_end=today + timedelta(days=18),
            status="To Do",
            importance=10,
            urgency=9,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
        Task(
            name="Data Collection: Historical Stock Market Data",
            duration_days=15,
            planned_start=today + timedelta(days=19),
            planned_end=today + timedelta(days=34),
            status="To Do",
            importance=10,
            urgency=10,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
        Task(
            name="Data Cleaning and Preprocessing",
            duration_days=20,
            planned_start=today + timedelta(days=35),
            planned_end=today + timedelta(days=55),
            status="To Do",
            importance=9,
            urgency=9,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
        Task(
            name="Feature Engineering and Selection",
            duration_days=15,
            planned_start=today + timedelta(days=56),
            planned_end=today + timedelta(days=71),
            status="To Do",
            importance=9,
            urgency=8,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
        Task(
            name="Model Development: Predictive Algorithms",
            duration_days=30,
            planned_start=today + timedelta(days=72),
            planned_end=today + timedelta(days=102),
            status="To Do",
            importance=10,
            urgency=9,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
        Task(
            name="Model Validation and Testing",
            duration_days=20,
            planned_start=today + timedelta(days=103),
            planned_end=today + timedelta(days=123),
            status="To Do",
            importance=10,
            urgency=8,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
        Task(
            name="System Integration and Deployment",
            duration_days=15,
            planned_start=today + timedelta(days=124),
            planned_end=today + timedelta(days=139),
            status="To Do",
            importance=9,
            urgency=7,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
        Task(
            name="Documentation: In-Code and External",
            duration_days=10,
            planned_start=today + timedelta(days=140),
            planned_end=today + timedelta(days=150),
            status="To Do",
            importance=8,
            urgency=7,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
        Task(
            name="Final Testing and Quality Assurance",
            duration_days=15,
            planned_start=today + timedelta(days=151),
            planned_end=today + timedelta(days=166),
            status="To Do",
            importance=10,
            urgency=8,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
        Task(
            name="Project Review and Closure",
            duration_days=7,
            planned_start=today + timedelta(days=167),
            planned_end=today + timedelta(days=174),
            status="To Do",
            importance=9,
            urgency=6,
            current_stage=backlog_stage,
            assigned_resources=[],
        ),
    ]
    for task in tasks:
        existing = Task.query.filter_by(name=task.name).first()
        if not existing:
            db.session.add(task)
    db.session.commit()

if __name__ == "__main__":
    with db.app.app_context():
        seed_initial_data()
