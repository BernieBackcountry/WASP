from pathlib import Path
import sys


def get_project_path() -> Path:
    return Path(sys.argv[0]).resolve().parent


def create_directory(path: Path):
    path.mkdir(parents=True, exist_ok=True)
