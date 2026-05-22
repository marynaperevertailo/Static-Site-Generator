import os
import shutil
import sys

from copystatic import copy_files_recursive
from page_generator import generate_pages_recursive

dir_path_static = "./static"
dir_path_docs = "./docs"
dir_path_content = "./content"
template_path = "./template.html"

default_basepath = "/"


def main():
    basepath = default_basepath
    if len(sys.argv) > 1:
        basepath = sys.argv[1]

    print("Deleting docs directory...")
    if os.path.exists(dir_path_docs):
        shutil.rmtree(dir_path_docs)

    print("Copying static files to docs directory...")
    copy_files_recursive(dir_path_static, dir_path_docs)

    print(f"Generating pages with basepath '{basepath}'...")
    generate_pages_recursive(dir_path_content, template_path, dir_path_docs, basepath)


main()
