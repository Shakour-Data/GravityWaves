#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path
import venv

import subprocess

def create_virtualenv(path: Path):
    if path.exists():
        print(f"Virtual environment already exists at: {path}")
        # Check and install requirements if needed
        req_file = path.parent / "requirements.txt"
        if req_file.exists():
            print(f"Installing requirements from {req_file} in existing virtualenv...")
            subprocess.run([str(path / "bin" / "pip"), "install", "-r", str(req_file)])
        else:
            print(f"No requirements.txt found in {req_file.parent}")
    else:
        print(f"Creating virtual environment at: {path}")
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(str(path))
        print(f"Virtual environment created at: {path}")
        # Install requirements after creation
        req_file = path.parent / "requirements.txt"
        if req_file.exists():
            print(f"Installing requirements from {req_file} in new virtualenv...")
            subprocess.run([str(path / "bin" / "pip"), "install", "-r", str(req_file)])
        else:
            print(f"No requirements.txt found in {req_file.parent}")

def setup_and_run_mcp_server():
    mcp_dir = Path(__file__).parent / "Docs" / "Initial_plan" / "mcp_json_creator_server"
    venv_dir = mcp_dir / ".venv"
    req_file = mcp_dir / "requirements.txt"
    server_script = mcp_dir / "server.py"  # Assumes the server entry point is server.py

    # Create virtual environment for the MCP server if it does not exist
    if not venv_dir.exists():
        print(f"Creating virtual environment for MCP server at: {venv_dir}")
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(str(venv_dir))
    else:
        print(f"Virtual environment for MCP server already exists at: {venv_dir}")

    # Install requirements if requirements.txt exists
    if req_file.exists():
        print(f"Installing requirements for MCP server from {req_file} ...")
        subprocess.run([str(venv_dir / "bin" / "pip"), "install", "-r", str(req_file)])
    else:
        print(f"No requirements.txt found for MCP server at {req_file}")

    # Run the server if the entry script exists
    if server_script.exists():
        print(f"Starting MCP server from {server_script} ...")
        subprocess.Popen([str(venv_dir / "bin" / "python"), str(server_script)])
        print("MCP server started in the background.")
    else:
        print(f"Server script not found at {server_script}")

def main():
    base_dir = Path(__file__).parent.resolve()

    # Define project directories relative to base_dir
    gravitywaves_dir = base_dir
    pln_project_dir = base_dir / "Docs" / "pln_GravityWavesProjectManagement"
    doc_project_dir = base_dir / "Docs" / "doc_GravityWavesDocumentation"
    initial_plan_dir = base_dir / "Docs" / "Initial_plan"

    # Define virtual environment directories
    gravitywaves_venv = gravitywaves_dir / ".venv"
    pln_venv = pln_project_dir / ".pln_venv"
    doc_venv = doc_project_dir / ".doc_venv"
    initial_plan_venv = initial_plan_dir / "int_pln_venv"

    # Create virtual environments for each project
    create_virtualenv(gravitywaves_venv)
    create_virtualenv(pln_venv)
    create_virtualenv(doc_venv)
    create_virtualenv(initial_plan_venv)

    # Setup and run the MCP server
    setup_and_run_mcp_server()

if __name__ == "__main__":
    main()
