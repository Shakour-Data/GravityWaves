import unittest
import json
import os
from datetime import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import update_dashboard

class TestProjectManagement(unittest.TestCase):
    TASKS_FILE = "Docs/Initial_plan/tasks.json"
    COMMITS_FILE = "Docs/Initial_plan/commits.json"
    IMPORTANCE_LEVELS_FILE = "Docs/Initial_plan/importance_levels.json"
    URGENCY_LEVELS_FILE = "Docs/Initial_plan/urgency_levels.json"
    DASHBOARD_FILE = "Docs/Initial_plan/Project_Dashboard.txt"

    def setUp(self):
        # Load JSON data for tests
        with open(self.TASKS_FILE, "r", encoding="utf-8") as f:
            self.tasks = json.load(f)
        with open(self.COMMITS_FILE, "r", encoding="utf-8") as f:
            self.commits = json.load(f)
        with open(self.IMPORTANCE_LEVELS_FILE, "r", encoding="utf-8") as f:
            self.importance_levels = json.load(f)
        with open(self.URGENCY_LEVELS_FILE, "r", encoding="utf-8") as f:
            self.urgency_levels = json.load(f)

    def test_load_json_files(self):
        # Test that JSON files load correctly and are not empty
        self.assertTrue(len(self.tasks) > 0, "Tasks JSON should not be empty")
        self.assertTrue(len(self.commits) > 0, "Commits JSON should not be empty")
        self.assertTrue(len(self.importance_levels) > 0, "Importance levels JSON should not be empty")
        self.assertTrue(len(self.urgency_levels) > 0, "Urgency levels JSON should not be empty")

    def test_summarize_tasks(self):
        summary = update_dashboard.summarize_tasks(self.tasks, self.importance_levels, self.urgency_levels)
        self.assertIn("total_tasks", summary)
        self.assertIn("completed_count", summary)
        self.assertIn("progress_percent", summary)
        self.assertIn("completed_tasks", summary)
        self.assertIn("important_tasks", summary)
        self.assertIn("urgent_tasks", summary)
        self.assertEqual(summary["total_tasks"], len(self.tasks))

    def test_format_task(self):
        task = self.tasks[0]
        formatted = update_dashboard.format_task(task, self.importance_levels, self.urgency_levels)
        self.assertIn(str(task["id"]), formatted)
        self.assertIn(task["name"], formatted)
        self.assertIn(task["status"], formatted)

    def test_dashboard_generation(self):
        # Run main function to generate dashboard file
        update_dashboard.main()
        self.assertTrue(os.path.exists(self.DASHBOARD_FILE), "Dashboard file should be created")

        # Check dashboard file content is not empty
        with open(self.DASHBOARD_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(len(content) > 0, "Dashboard file should not be empty")

    def test_dashboard_content_consistency(self):
        # Generate dashboard content
        update_dashboard.main()
        with open(self.DASHBOARD_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that total tasks count is in dashboard content
        total_tasks = len(self.tasks)
        self.assertIn(f"Total Tasks: {total_tasks}", content)

        # Check that completed tasks count is in dashboard content
        completed_tasks = len([t for t in self.tasks if t["status"].lower() == "done"])
        self.assertIn(f"Completed Tasks: {completed_tasks}", content)

if __name__ == "__main__":
    unittest.main()
