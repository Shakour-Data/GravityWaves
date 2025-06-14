import os
import json
import unittest
from Docs.Initial_plan.scripts import project_management_system as pms

class TestProjectManagementSystem(unittest.TestCase):
    TEST_BASE_DIR = "Docs/Initial_plan/tests/test_data"

    def setUp(self):
        # Create test directories
        os.makedirs(os.path.join(self.TEST_BASE_DIR, "projects"), exist_ok=True)
        os.makedirs(os.path.join(self.TEST_BASE_DIR, "subprojects_l1"), exist_ok=True)
        os.makedirs(os.path.join(self.TEST_BASE_DIR, "subprojects_l2"), exist_ok=True)
        os.makedirs(os.path.join(self.TEST_BASE_DIR, "activities_l1"), exist_ok=True)
        os.makedirs(os.path.join(self.TEST_BASE_DIR, "activities_l2"), exist_ok=True)
        os.makedirs(os.path.join(self.TEST_BASE_DIR, "tasks"), exist_ok=True)

        # Override base dir for testing
        pms.BASE_DIR = self.TEST_BASE_DIR

    def tearDown(self):
        # Clean up test directories and files
        import shutil
        if os.path.exists(self.TEST_BASE_DIR):
            shutil.rmtree(self.TEST_BASE_DIR)

    def test_create_and_load_project_file(self):
        project_id = "proj1"
        project_data = {
            "id": project_id,
            "name": "Test Project",
            "description": "A test project",
            "status": "To Do"
        }
        pms.create_project_file(project_id, project_data)
        path = os.path.join(self.TEST_BASE_DIR, "projects", f"{project_id}.json")
        self.assertTrue(os.path.exists(path))
        loaded = pms.load_json_file(path)
        self.assertEqual(loaded["id"], project_id)
        self.assertEqual(loaded["name"], "Test Project")

    def test_process_hierarchy_creates_all_files(self):
        hierarchy = {
            "projects": {
                "proj1": {"id": "proj1", "name": "Project 1"}
            },
            "subprojects_l1": {
                "sub1": {"id": "sub1", "name": "Subproject L1"}
            },
            "subprojects_l2": {
                "sub2": {"id": "sub2", "name": "Subproject L2"}
            },
            "activities_l1": {
                "act1": {"id": "act1", "name": "Activity L1"}
            },
            "activities_l2": {
                "act2": {"id": "act2", "name": "Activity L2"}
            },
            "tasks": {
                "task1": {"id": "task1", "name": "Task 1"}
            },
            "main_core": {
                "id": "main_core",
                "description": "Main core data"
            }
        }
        pms.process_hierarchy(hierarchy)
        # Check files exist
        self.assertTrue(os.path.exists(os.path.join(self.TEST_BASE_DIR, "projects", "proj1.json")))
        self.assertTrue(os.path.exists(os.path.join(self.TEST_BASE_DIR, "subprojects_l1", "sub1.json")))
        self.assertTrue(os.path.exists(os.path.join(self.TEST_BASE_DIR, "subprojects_l2", "sub2.json")))
        self.assertTrue(os.path.exists(os.path.join(self.TEST_BASE_DIR, "activities_l1", "act1.json")))
        self.assertTrue(os.path.exists(os.path.join(self.TEST_BASE_DIR, "activities_l2", "act2.json")))
        self.assertTrue(os.path.exists(os.path.join(self.TEST_BASE_DIR, "tasks", "task1.json")))
        self.assertTrue(os.path.exists(os.path.join(self.TEST_BASE_DIR, "main_core.json")))

if __name__ == "__main__":
    unittest.main()
