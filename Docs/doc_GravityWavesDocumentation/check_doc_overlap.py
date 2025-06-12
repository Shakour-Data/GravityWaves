import os

def get_all_paths(root_dir):
    paths = set()
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            rel_dir = os.path.relpath(os.path.join(dirpath, dirname), root_dir)
            paths.add(rel_dir)
        for filename in filenames:
            rel_file = os.path.relpath(os.path.join(dirpath, filename), root_dir)
            paths.add(rel_file)
    return paths

def main():
    doc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    project_management_dir = os.path.abspath(os.path.join(doc_dir, '../../Docs/pln_GravityWavesProjectManagement'))
    main_project_dir = os.path.abspath(os.path.join(doc_dir, '../../app'))

    print(f"Checking overlaps between documentation site and project management and main project directories...\n")

    doc_paths = get_all_paths(doc_dir)
    pm_paths = get_all_paths(project_management_dir)
    main_paths = get_all_paths(main_project_dir)

    overlap_pm = doc_paths.intersection(pm_paths)
    overlap_main = doc_paths.intersection(main_paths)

    if overlap_pm:
        print("Warning: Overlapping files/folders found between documentation and project management:")
        for path in sorted(overlap_pm):
            print(f"  {path}")
    else:
        print("No overlaps found between documentation and project management.")

    if overlap_main:
        print("Warning: Overlapping files/folders found between documentation and main project:")
        for path in sorted(overlap_main):
            print(f"  {path}")
    else:
        print("No overlaps found between documentation and main project.")

if __name__ == "__main__":
    main()
