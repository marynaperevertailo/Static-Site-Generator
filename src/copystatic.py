import os
import shutil


def copy_files_recursive(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    for entry in os.listdir(source_dir):
        source_path = os.path.join(source_dir, entry)
        dest_path = os.path.join(dest_dir, entry)
        print(f" * {source_path} -> {dest_path}")
        if os.path.isfile(source_path):
            shutil.copy(source_path, dest_path)
        else:
            copy_files_recursive(source_path, dest_path)
