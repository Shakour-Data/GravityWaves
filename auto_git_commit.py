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

import subprocess

def get_file_diff_summary(file_path):
    """Get a short summary of changes for a file."""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged", "--", file_path],
            capture_output=True,
            text=True,
            check=True,
        )
        diff_lines = result.stdout.strip().splitlines()
        # Return first 5 lines or less as summary
        summary = "\n    ".join(diff_lines[:5]) if diff_lines else "No diff available."
        return summary
    except subprocess.CalledProcessError:
        return "Could not retrieve diff."

def generate_commit_message(group_name, category_name, files):
    """Generate commit message for a specific file group and category."""
    friendly_category = {
        "Added": "✨ This file was newly added to the project and is now tracked.",
        "Modified": "🛠️ This file was modified with updates or fixes.",
        "Deleted": "🗑️ This file was removed from the project.",
        "Renamed": "🔀 This file was renamed or moved to a different location.",
        "Copied": "📋 This file was copied from another file.",
        "Updated but unmerged": "⚠️ This file has merge conflicts that need to be resolved.",
        "Untracked": "🆕 This file is new and not yet tracked by git.",
        "Ignored": "🚫 This file is ignored by git.",
        "Added and Modified": "✨🛠️ This file was added and then modified before committing.",
        "Deleted and Modified": "🗑️🛠️ This file was deleted and modified before committing.",
        "Renamed and Modified": "🔀🛠️ This file was renamed and modified before committing.",
        "Copied and Modified": "📋🛠️ This file was copied and modified before committing.",
        "Unmerged": "⚠️ This file has unmerged changes.",
        "Type Changed": "🔄 The file type has changed.",
        "Unknown": "❓ This file has an unknown change status.",
        "Other": "⚙️ This file has other types of changes.",
        "Conflicted": "❗ This file has conflicts that need to be resolved.",
        "Staged": "📌 This file is staged for commit.",
        "Unstaged": "✏️ This file has unstaged changes.",
        "Both Modified": "🛠️ This file was modified in both the index and working tree.",
    }
    description = friendly_category.get(category_name, "")
    message = f"Auto Commit for group: {group_name} - {category_name}\n\n"
    if description:
        message += f"Files in this category:\n\n"
    message += f"Reason for changes: [Please describe the reason or issue addressed by these changes]\n\n"
    for f in files:
        message += f"  - {f}: {description}\n"
        diff_summary = get_file_diff_summary(f)
        message += f"    Summary of changes:\n    {diff_summary}\n\n"
    return message

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

            change_descriptions = {
                "Added": "This file was newly added to the project and is now tracked.",
                "Modified": "This file was modified with updates or fixes.",
                "Deleted": "This file was removed from the project.",
                "Renamed": "This file was renamed or moved to a different location.",
                "Untracked": "This file is new and not yet tracked by git.",
                "Other": "This file has other types of changes.",
            }
            description = change_descriptions.get(category_name, "")
            commit_message = f"Auto Commit for group: {group_name} - {category_name}\n\n"
            if description:
                commit_message += f"Files in this category:\n\n"
            commit_message += "Reason for changes: [Please describe the reason or issue addressed by these changes]\n\n"
            for f in category_files:
                commit_message += f"  - {f}: {description}\n"

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
