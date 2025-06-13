from flask import Flask
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from pln_app import app, db, Task, Resource, WorkCycleStage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed default stages
            stages = [
                {"name": "Backlog", "description": "Task is in backlog", "order": 1},
                {"name": "To Do", "description": "Task ready to start", "order": 2},
                {"name": "In Progress", "description": "Task is being worked on", "order": 3},
                {"name": "Code Review", "description": "Task is under code review", "order": 4},
                {"name": "Testing", "description": "Task is being tested", "order": 5},
                {"name": "Done", "description": "Task is completed", "order": 6},
            ]
            for stage in stages:
                db.session.add(WorkCycleStage(**stage))
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_index_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'pln_index.html' in rv.data or b'Project' in rv.data

def test_api_work_cycle_stages(client):
    rv = client.get('/api/work_cycle_stages')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, list)
    assert any(stage['name'] == 'Backlog' for stage in data)

def test_api_tasks_get_empty(client):
    rv = client.get('/api/tasks')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data == []

def test_api_tasks_post_and_get(client):
    # First create a resource
    resource_data = {"name": "Developer", "hourly_rate": 50.0, "type": "human"}
    rv = client.post('/api/resources', json=resource_data)
    assert rv.status_code == 201
    resource = rv.get_json()['resource']

    # Create a project
    with app.app_context():
        from pln_app import Project
        project = Project(name="Test Project")
        db.session.add(project)
        db.session.commit()
        project_id = project.id

    # Create a task
    task_data = {
        "project_id": project_id,
        "name": "Test Task",
        "duration_days": 5,
        "planned_start": "2024-01-01",
        "planned_end": "2024-01-06",
        "actual_start": None,
        "actual_end": None,
        "status": "To Do",
        "importance": 5,
        "urgency": 5,
        "current_stage_id": None,
        "assigned_resources": [resource['id']]
    }
    rv = client.post('/api/tasks', json=task_data)
    assert rv.status_code == 201
    task = rv.get_json()['task']
    assert task['name'] == "Test Task"
    assert len(task['assigned_resources']) == 1

    # Get tasks and verify
    rv = client.get('/api/tasks')
    assert rv.status_code == 200
    tasks = rv.get_json()
    assert any(t['name'] == "Test Task" for t in tasks)

def test_api_resources_get_empty(client):
    rv = client.get('/api/resources')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, list)

def test_api_resources_post_and_get(client):
    resource_data = {"name": "Tester", "hourly_rate": 40.0, "type": "human"}
    rv = client.post('/api/resources', json=resource_data)
    assert rv.status_code == 201
    resource = rv.get_json()['resource']
    assert resource['name'] == "Tester"

    rv = client.get('/api/resources')
    assert rv.status_code == 200
    resources = rv.get_json()
    assert any(r['name'] == "Tester" for r in resources)

import datetime

def test_api_import_commits(client):
    # Setup task
    with app.app_context():
        from pln_app import Task
        project = db.session.query(Task).first()
        if not project:
            from pln_app import Project
            project = Project(name="Commit Project")
            db.session.add(project)
            db.session.commit()
        task = Task.query.first()
        if not task:
            task = Task(
                project_id=project.id,
                name="Commit Task",
                duration_days=1,
                planned_start=datetime.date(2024, 1, 1),
                planned_end=datetime.date(2024, 1, 2),
                status="To Do",
                importance=1,
                urgency=1
            )
            db.session.add(task)
            db.session.commit()

        commits_data = [
            {
                "commit_hash": "abc123",
                "message": "Initial commit",
                "author": "Tester",
                "date": "2024-01-01T12:00:00",
                "task_id": task.id
            },
            {
                "commit_hash": "def456",
                "message": "done feature",
                "author": "Tester",
                "date": "2024-01-02T12:00:00",
                "task_id": task.id
            }
        ]
    rv = client.post('/api/import_commits', json=commits_data)
    assert rv.status_code == 201
    data = rv.get_json()
    assert "Imported" in data['message']

def test_api_ai_summary_report(client):
    rv = client.get('/api/reports/ai_summary')
    assert rv.status_code == 200
    data = rv.get_json()
    assert "stage_summary" in data
    assert "urgent_tasks" in data
    assert "important_tasks" in data
    assert "next_recommended_activities" in data

# New tests for error handling and additional coverage

def test_api_tasks_post_invalid_data(client):
    # Missing required fields
    invalid_data = {"name": "Invalid Task"}
    rv = client.post('/api/tasks', json=invalid_data)
    assert rv.status_code == 400
    assert "error" in rv.get_json()

def test_api_resources_post_invalid_data(client):
    # Missing required fields
    invalid_data = {"name": "Invalid Resource"}
    rv = client.post('/api/resources', json=invalid_data)
    assert rv.status_code == 400
    assert "error" in rv.get_json()

def test_api_import_commits_invalid_data(client):
    # Not a list
    invalid_data = {"commit_hash": "abc123"}
    rv = client.post('/api/import_commits', json=invalid_data)
    assert rv.status_code == 400
    assert "error" in rv.get_json()

def test_api_commits_get(client):
    rv = client.get('/api/commits')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, list)
