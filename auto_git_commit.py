import os
import subprocess
from collections import defaultdict

def run_git_command(args):
    """Run a git command and return (success, output)."""
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: git {' '.join(args)}")
        print(f"Error: {e.stderr.strip()}")
        return False, e.stderr.strip()

def get_git_changes():
    """Fetch Git status and return list of changes."""
    success, output = run_git_command(["status", "--short"])
    if not success:
        return []
    return output.splitlines()

def group_related_files(changes):
    """Group files based on top-level directory (code relationship)."""
    groups = defaultdict(list)

    for change in changes:
        if not change:
            continue
        # Handle untracked files starting with '??'
        if change.startswith("??"):
            status = "??"
            file_path = change[2:].lstrip()
        else:
            # Split line into status and file path
            parts = change.split(None, 1)
            if len(parts) == 2:
                status, file_path = parts[0], parts[1].lstrip()
            else:
                status = parts[0]
                file_path = ""

        # For renamed files, file_path contains "old_path -> new_path"
        if status == "R":
            parts = file_path.split("->")
            if len(parts) == 2:
                old_path = parts[0].strip()
                new_path = parts[1].strip()
                # Group by new_path
                file_path = new_path
            else:
                # fallback
                file_path = file_path.strip()

        # Determine top-level directory or root if none
        parts = file_path.split(os.sep)
        if len(parts) > 1:
            top_level_dir = parts[0]
        else:
            top_level_dir = "root"

        # Debug print to verify file paths
        print(f"Status: {status}, File path: '{file_path}'")

        groups[top_level_dir].append((status, file_path))

    return groups

def categorize_files(files):
    """Categorize files into different change types."""
    categories = defaultdict(list)

    for status, file in files:
        if status == "A":
            categories["Added"].append(file)
        elif status == "M":
            categories["Modified"].append(file)
        elif status == "D":
            categories["Deleted"].append(file)
        elif status == "R":
            categories["Renamed"].append(file)
        elif status == "??":
            categories["Untracked"].append(file)
        else:
            categories["Other"].append(file)

    return categories

def generate_commit_message(group_name, categories):
    """Generate commit message for a specific file group."""
    message = f"Auto Commit for group: {group_name}\n\n"
    for category, files in categories.items():
        if files:
            # Friendly category names
            friendly_category = {
                "A": "Added",
                "M": "Modified",
                "D": "Deleted",
                "R": "Renamed",
                "??": "Untracked",
                "Untracked": "Untracked",
                "Added": "Added",
                "Modified": "Modified",
                "Deleted": "Deleted",
                "Renamed": "Renamed",
                "Other": "Other",
            }.get(category, category)

            message += f"{friendly_category} files:\n"
            for f in files:
                message += f"  - {f}\n"
            message += "\n"
    return message.strip()

def auto_commit_and_push():
    """Automate Git commit and push process in groups and categories."""
    changes = get_git_changes()
    if not changes or (len(changes) == 1 and changes[0] == ''):
        print("No changes detected.")
        return

    grouped_files = group_related_files(changes)

    for group_name, files in grouped_files.items():
        categories = categorize_files(files)

        for category_name, category_files in categories.items():
            if not category_files:
                continue

            commit_message = f"Auto Commit for group: {group_name} - {category_name}\n\n"
            commit_message += f"{category_name} files:\n"
            for f in category_files:
                commit_message += f"  - {f}\n"

            # Stage only the files in this category
            success, _ = run_git_command(["add"] + category_files)
            if not success:
                print(f"Failed to stage files for {group_name} - {category_name}. Skipping commit.")
                continue

            # Commit with the generated message
            success, _ = run_git_command(["commit", "-m", commit_message])
            if not success:
                print(f"Failed to commit files for {group_name} - {category_name}. Skipping push.")
                continue

            # Push the commit
            success, _ = run_git_command(["push"])
            if not success:
                print(f"Failed to push commit for {group_name} - {category_name}.")
                continue

            print(f"Committed and pushed changes for group: {group_name} - category: {category_name}")

if __name__ == "__main__":
    auto_commit_and_push()
