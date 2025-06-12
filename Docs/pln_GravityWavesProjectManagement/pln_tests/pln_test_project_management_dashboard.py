import pytest
import sys
import os
from datetime import date

# Adjust sys.path to import pln_app from Docs/pln_GravityWavesProjectManagement
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pln_app import app, db, Task, Resource, WorkCycleStage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed minimal data for tests
            stage = WorkCycleStage(name="Backlog", order=1)
            db.session.add(stage)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'GravityWaves Project Management' in response.data

def test_get_tasks_empty(client):
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert response.get_json() == []

def test_add_task(client):
    with app.app_context():
        stage = WorkCycleStage.query.first()
    task_data = {
        "name": "Test Task",
        "duration_days": 5,
        "planned_start": date.today().strftime("%Y-%m-%d"),
        "planned_end": (date.today()).strftime("%Y-%m-%d"),
        "status": "To Do",
        "importance": 5,
        "urgency": 5,
        "current_stage_id": stage.id,
        "assigned_resource_ids": []
    }
    response = client.post('/api/tasks', json=task_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data["task"]["name"] == "Test Task"
    assert data["task"]["status"] == "To Do"

def test_get_resources_empty(client):
    response = client.get('/api/resources')
    assert response.status_code == 200
    assert response.get_json() == []

def test_add_resource(client):
    resource_data = {
        "name": "Test Resource",
        "hourly_rate": 50.0,
        "type": "human"
    }
    response = client.post('/api/resources', json=resource_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data["resource"]["name"] == "Test Resource"
    assert data["resource"]["hourly_rate"] == 50.0

def test_get_work_cycle_stages(client):
    with app.app_context():
        stage = WorkCycleStage(name="To Do", order=2)
        db.session.add(stage)
        db.session.commit()
    response = client.get('/api/work_cycle_stages')
    assert response.status_code == 200
    stages = response.get_json()
    assert any(s["name"] == "To Do" for s in stages)

def test_import_commits(client):
    with app.app_context():
        stage = WorkCycleStage.query.first()
        task = Task(name="Commit Task", duration_days=1, planned_start=date.today(), planned_end=date.today(), current_stage=stage)
        db.session.add(task)
        db.session.commit()
        commit_data = [{
            "commit_hash": "abc123",
            "message": "Initial commit",
            "author": "Tester",
            "date": date.today().isoformat(),
            "task_id": task.id
        }]
    response = client.post('/api/import_commits', json=commit_data)
    assert response.status_code == 201
    data = response.get_json()
    assert "Imported" in data["message"]

def test_ai_summary_report(client):
    response = client.get('/api/reports/ai_summary')
    assert response.status_code == 200
    data = response.get_json()
    assert "stage_summary" in data
    assert "urgent_tasks" in data
    assert "important_tasks" in data
    assert "next_recommended_activities" in data
