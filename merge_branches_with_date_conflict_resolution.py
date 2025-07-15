import subprocess
import sys

def run_git_command(args, capture_output=True):
    try:
        result = subprocess.run(["git"] + args, capture_output=capture_output, text=True, check=True)
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: git {' '.join(args)}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return None

def get_branches_sorted_by_commit_date():
    branches = run_git_command(["for-each-ref", "--sort=-committerdate", "--format=%(refname:short)", "refs/heads/"])
    if branches is None:
        sys.exit("Failed to get branches")
    branch_list = branches.splitlines()
    if "main" in branch_list:
        branch_list.remove("main")
    return branch_list

def get_last_commit_date(branch, file_path):
    # Get last commit date (unix timestamp) for a file in a branch
    date_str = run_git_command(["log", "-1", "--format=%ct", branch, "--", file_path])
    if date_str is None:
        return 0
    return int(date_str)

def resolve_conflicts_by_date(branch, main_branch="main"):
    # Get list of conflicting files
    conflict_files = run_git_command(["diff", "--name-only", "--diff-filter=U"])
    if not conflict_files:
        return True  # No conflicts

    conflict_files_list = conflict_files.splitlines()
    print(f"Conflicts detected in files: {conflict_files_list}")

    for file_path in conflict_files_list:
        # Get last commit date for the file in both branches
        branch_date = get_last_commit_date(branch, file_path)
        main_date = get_last_commit_date(main_branch, file_path)

        print(f"File: {file_path}, {branch} date: {branch_date}, {main_branch} date: {main_date}")

        # Choose the version with the more recent commit date
        if branch_date >= main_date:
            # Use branch version (theirs)
            print(f"Choosing {branch} version for {file_path}")
            # Checkout theirs version
            subprocess.run(["git", "checkout", "--theirs", file_path], check=True)
        else:
            # Use main version (ours)
            print(f"Choosing {main_branch} version for {file_path}")
            # Checkout ours version
            subprocess.run(["git", "checkout", "--ours", file_path], check=True)

        # Add resolved file
        subprocess.run(["git", "add", file_path], check=True)

    # Commit the merge with resolved conflicts
    commit_message = f"Merge branch '{branch}' into {main_branch} with conflict resolution by commit date"
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    print(f"Conflicts resolved and committed for branch {branch}")
    return True

def main():
    main_branch = "main"
    # Fetch all branches and commits
    subprocess.run(["git", "fetch", "--all"], check=True)

    # Checkout main branch
    subprocess.run(["git", "checkout", main_branch], check=True)

    branches = get_branches_sorted_by_commit_date()
    print(f"Branches to merge: {branches}")

    for branch in branches:
        print(f"Merging branch: {branch}")
        # Try to merge branch
        result = subprocess.run(["git", "merge", "--no-ff", branch], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Branch {branch} merged successfully.")
        else:
            print(f"Merge conflicts detected when merging {branch}. Resolving by commit date...")
            resolved = resolve_conflicts_by_date(branch, main_branch)
            if not resolved:
                print(f"Failed to resolve conflicts for branch {branch}. Aborting.")
                sys.exit(1)

    print("All branches merged into main with conflict resolution by commit date.")

if __name__ == "__main__":
    main()
