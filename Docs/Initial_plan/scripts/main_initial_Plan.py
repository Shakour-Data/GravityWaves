#!/usr/bin/env python3
import os
import sys
import subprocess

def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error running {script_name}:")
        print(result.stderr)
        sys.exit(1)

def main():
    base_folder = os.path.dirname(os.path.abspath(__file__))
    print("Starting initial setup of the project management system...")

    # Step 1: Run project management system script to guide user through initial setup
    project_management_system_script = os.path.join(base_folder, "project_management_system.py")
    run_script(project_management_system_script)

    # Step 2: Inform user about next steps
    print("\nInitial setup complete.")
    print("Next steps:")
    print("- Decompose projects into subprojects and activities with user approval.")
    print("- Generate corresponding JSON files for each level.")
    print("- Integrate with existing Python scripts for dashboard and reporting.")
    print("- Automate commit hook integration for dynamic updates.")

if __name__ == "__main__":
    main()
