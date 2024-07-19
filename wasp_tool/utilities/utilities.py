"""
This module contains general functions for navigating and creating directories.

FUNCTIONS
    get_project_path()
        Return a new path object representing the current directory.
    create_directory(path: Path)
        Create a new directory at the given path.
"""
from pathlib import Path


def get_project_path() -> Path:
    """
    Return a new path object representing the current directory.

    Returns
    -------
    Path
        Concrete path for the current directory
    """
    return Path.cwd()


def create_directory(path: Path):
    """
    Create a new directory at the given path.

    Parameters
    ----------
    path: Path
        Concrete path for the new directory
    """
    path.mkdir(parents=True, exist_ok=True)
