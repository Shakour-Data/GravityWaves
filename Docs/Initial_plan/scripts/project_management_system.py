import os
import json

BASE_DIR = "Docs/Initial_plan/data"

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_project_file(project_id, project_data):
    path = os.path.join(BASE_DIR, "projects", f"{project_id}.json")
    save_json_file(path, project_data)

def create_subproject_l1_file(subproject_id, subproject_data):
    path = os.path.join(BASE_DIR, "subprojects_l1", f"{subproject_id}.json")
    save_json_file(path, subproject_data)

def create_subproject_l2_file(subproject_id, subproject_data):
    path = os.path.join(BASE_DIR, "subprojects_l2", f"{subproject_id}.json")
    save_json_file(path, subproject_data)

def create_activity_l1_file(activity_id, activity_data):
    path = os.path.join(BASE_DIR, "activities_l1", f"{activity_id}.json")
    save_json_file(path, activity_data)

def create_activity_l2_file(activity_id, activity_data):
    path = os.path.join(BASE_DIR, "activities_l2", f"{activity_id}.json")
    save_json_file(path, activity_data)

def create_task_file(task_id, task_data):
    path = os.path.join(BASE_DIR, "tasks", f"{task_id}.json")
    save_json_file(path, task_data)

def create_main_core_file(main_core_data):
    path = os.path.join(BASE_DIR, "main_core.json")
    save_json_file(path, main_core_data)

# Example function to process and create all files from a hierarchical input
def process_hierarchy(hierarchy):
    # hierarchy is expected to be a dict with keys: projects, subprojects_l1, subprojects_l2, activities_l1, activities_l2, tasks
    for project_id, project_data in hierarchy.get("projects", {}).items():
        create_project_file(project_id, project_data)

    for subproject_id, subproject_data in hierarchy.get("subprojects_l1", {}).items():
        create_subproject_l1_file(subproject_id, subproject_data)

    for subproject_id, subproject_data in hierarchy.get("subprojects_l2", {}).items():
        create_subproject_l2_file(subproject_id, subproject_data)

    for activity_id, activity_data in hierarchy.get("activities_l1", {}).items():
        create_activity_l1_file(activity_id, activity_data)

    for activity_id, activity_data in hierarchy.get("activities_l2", {}).items():
        create_activity_l2_file(activity_id, activity_data)

    for task_id, task_data in hierarchy.get("tasks", {}).items():
        create_task_file(task_id, task_data)

    main_core_data = hierarchy.get("main_core", {})
    if main_core_data:
        create_main_core_file(main_core_data)

if __name__ == "__main__":
    # Example usage: load a hierarchical JSON input and process it
    input_path = os.path.join(BASE_DIR, "hierarchy_input.json")
    if os.path.exists(input_path):
        hierarchy = load_json_file(input_path)
        process_hierarchy(hierarchy)
        print("Hierarchy JSON files created successfully.")
    else:
        print(f"Input file {input_path} not found.")
