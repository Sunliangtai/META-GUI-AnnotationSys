import shutil
from utils import read_file, write_file
import os


def remove_if_exist(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove


from_path = os.path.join("../", "frontend", "dist")

# remove origin

