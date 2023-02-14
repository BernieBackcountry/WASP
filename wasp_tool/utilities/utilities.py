from pathlib import Path


def get_project_path() -> Path:
    return Path.cwd()


def create_directory(path: Path):
    path.mkdir(parents=True, exist_ok=True)
