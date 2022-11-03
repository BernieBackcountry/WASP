from pathlib import Path
import sys


def get_project_path() -> Path:
    return Path(sys.argv[0]).resolve().parent
