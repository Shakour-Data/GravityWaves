#!/usr/bin/env python3
"""
Main script to generate initial documentation for the GravityWaves project.

This script runs the doc_generator.py script with multiple input directories
(app/services and templates) and outputs the generated markdown documentation
to a specified output directory.
"""

import subprocess
import os

def main():
    input_paths = [
        "app/services",
        "templates"
    ]
    output_dir = "Docs/Initial_Documentation/generated_docs"

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cmd = [
        "python3",
        "Docs/Initial_Documentation/doc_generator.py",
        *input_paths,
        "--output_dir",
        output_dir
    ]

    print(f"Running documentation generation with command:\n{' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("Documentation generation completed successfully.")
        print(f"Generated docs are located in: {output_dir}")
    else:
        print("Documentation generation failed.")
        print("Error output:")
        print(result.stderr)

if __name__ == "__main__":
    main()
