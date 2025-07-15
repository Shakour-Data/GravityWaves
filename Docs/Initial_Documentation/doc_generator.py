import os
import argparse
import subprocess
import json

def collect_code_files(input_paths):
    """
    Collect all source code files from the given list of input paths.

    Args:
        input_paths (list of str): List of file or folder paths.

    Returns:
        list of str: List of source code file paths.
    """
    code_files = []
    for path in input_paths:
        if os.path.isfile(path):
            # If path is a file, add directly if it has a source code extension
            if path.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php', '.html')):
                code_files.append(path)
        elif os.path.isdir(path):
            # If path is a directory, walk recursively and add source code files
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php', '.html')):
                        code_files.append(os.path.join(root, file))
    return code_files

def generate_documentation(code_files, output_dir):
    """
    Generate markdown documentation files from a list of source code files.

    Args:
        code_files (list of str): List of source code file paths.
        output_dir (str): Directory where generated markdown documentation files will be saved.

    The current implementation is a minimal viable product (MVP) that creates placeholder
    documentation files. It can be extended to integrate AI-powered documentation generation.
    """
    for code_path in code_files:
        filename = os.path.basename(code_path)
        doc_filename = os.path.splitext(filename)[0] + "_doc.md"
        doc_filepath = os.path.join(output_dir, doc_filename)

        with open(doc_filepath, "w", encoding="utf-8") as f:
            f.write(f"# Documentation for {filename}\n\n")
            f.write(f"Generated documentation content for {filename}.\n")

        print(f"Generated documentation: {doc_filepath}")

def main():
    """
    Main entry point for the script.

    Parses command-line arguments for multiple input paths and output directory,
    ensures the output directory exists, collects source code files, and generates documentation.
    """
    parser = argparse.ArgumentParser(description="Generate markdown documentation from code files or folders.")
    parser.add_argument(
        "input_paths",
        nargs="+",
        help="Paths to source code files or folders to generate documentation for."
    )
    parser.add_argument(
        "--output_dir",
        default="Docs/Initial_Documentation/generated_docs",
        help="Directory to save generated markdown files (default: Docs/Initial_Documentation/generated_docs)."
    )
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    code_files = collect_code_files(args.input_paths)
    generate_documentation(code_files, args.output_dir)

if __name__ == "__main__":
    main()
