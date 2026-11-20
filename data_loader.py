"""
data_loader.py
Loads and validates career roles and student profiles from local JSON files.

Separates data loading and schema validation from scoring and business logic.
"""

import json
from pathlib import Path
from typing import List, Optional
from models import CareerRole, StudentProfile


# Default data file paths relative to project root
DEFAULT_ROLES_PATH = Path(__file__).resolve().parent / "career_roles.json"
DEFAULT_STUDENTS_PATH = Path(__file__).resolve().parent / "students.json"


def load_career_roles(file_path: Optional[Path] = None) -> List[CareerRole]:
    """
    Load career roles from a JSON file and validate with Pydantic.

    Args:
        file_path: Optional Path to the career_roles.json file.

    Returns:
        List of validated CareerRole instances.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If JSON is invalid or fails schema validation.
    """
    path = file_path or DEFAULT_ROLES_PATH
    if not path.exists():
        raise FileNotFoundError(f"Career roles file not found at: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Corrupted or invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw_data, list):
        raise ValueError(f"Expected a list of career roles in {path}, got {type(raw_data).__name__}")

    roles = [CareerRole.model_validate(item) for item in raw_data]
    return roles


def load_students(file_path: Optional[Path] = None) -> List[StudentProfile]:
    """
    Load student profiles from a JSON file and validate with Pydantic.

    Args:
        file_path: Optional Path to the students.json file.

    Returns:
        List of validated StudentProfile instances.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If JSON is invalid or fails schema validation.
    """
    path = file_path or DEFAULT_STUDENTS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Students profile file not found at: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Corrupted or invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw_data, list):
        raise ValueError(f"Expected a list of student profiles in {path}, got {type(raw_data).__name__}")

    students = [StudentProfile.model_validate(item) for item in raw_data]
    return students


def get_sample_student(name: str = "Harsha", file_path: Optional[Path] = None) -> StudentProfile:
    """
    Retrieve a sample student profile by name.

    Args:
        name: Name of the sample student (default: Harsha).
        file_path: Optional Path to students.json.

    Returns:
        The matched StudentProfile.

    Raises:
        KeyError: If student with specified name is not found.
    """
    students = load_students(file_path)
    for s in students:
        if s.name.lower() == name.lower():
            return s
    if students:
        return students[0]
    raise KeyError(f"No student profile found with name '{name}'")
