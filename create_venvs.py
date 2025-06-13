#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path
import venv

def create_virtualenv(path: Path):
    if path.exists():
        print(f"Virtual environment already exists at: {path}")
    else:
        print(f"Creating virtual environment at: {path}")
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(str(path))
        print(f"Virtual environment created at: {path}")

def main():
    base_dir = Path(__file__).parent.resolve()

    # Define project directories relative to base_dir
    gravitywaves_dir = base_dir
    pln_project_dir = base_dir / "Docs" / "pln_GravityWavesProjectManagement"
    doc_project_dir = base_dir / "Docs" / "doc_GravityWavesDocumentation"

    # Define virtual environment directories
    gravitywaves_venv = gravitywaves_dir / ".venv"
    pln_venv = pln_project_dir / ".pln_venv"
    doc_venv = doc_project_dir / ".doc_venv"

    create_virtualenv(gravitywaves_venv)
    create_virtualenv(pln_venv)
    create_virtualenv(doc_venv)

if __name__ == "__main__":
    main()
