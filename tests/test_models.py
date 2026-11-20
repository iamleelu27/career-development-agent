"""
tests/test_models.py
Tests for Pydantic data models and input validation.
"""

import pytest
from pydantic import ValidationError
from models import StudentProfile, SkillRequirement, CareerRole


def test_valid_student_profile():
    """Verify that a well-formed StudentProfile instantiates cleanly."""
    student = StudentProfile(
        name="Harsha",
        degree="B.Tech Computer Science",
        skills={"Python": 7.0, "Cloud": 5.0},
        interests=["Cloud", "AI"],
        existing_projects=["Chatbot"],
        available_weekly_hours=8.0,
        learning_timeframe_months=6
    )
    assert student.name == "Harsha"
    assert student.skills["Python"] == 7.0
    assert student.learning_timeframe_months == 6


def test_invalid_skill_proficiency_negative():
    """Proficiency below 0 must fail validation."""
    with pytest.raises(ValidationError) as exc_info:
        StudentProfile(
            name="Test Student",
            degree="CS",
            skills={"Python": -1.0}
        )
    assert "between 0 and 10" in str(exc_info.value)


def test_invalid_skill_proficiency_exceeds_ten():
    """Proficiency above 10 must fail validation."""
    with pytest.raises(ValidationError) as exc_info:
        StudentProfile(
            name="Test Student",
            degree="CS",
            skills={"Python": 11.0}
        )
    assert "between 0 and 10" in str(exc_info.value)


def test_invalid_learning_timeframe():
    """Learning timeframe outside 1-24 months must fail validation."""
    with pytest.raises(ValidationError):
        StudentProfile(
            name="Test Student",
            degree="CS",
            learning_timeframe_months=0
        )

    with pytest.raises(ValidationError):
        StudentProfile(
            name="Test Student",
            degree="CS",
            learning_timeframe_months=25
        )


def test_invalid_skill_requirement_bounds():
    """SkillRequirement must enforce importance 1-5 and target 1-10."""
    with pytest.raises(ValidationError):
        SkillRequirement(name="Python", importance=0, target_proficiency=8)

    with pytest.raises(ValidationError):
        SkillRequirement(name="Python", importance=6, target_proficiency=8)

    with pytest.raises(ValidationError):
        SkillRequirement(name="Python", importance=3, target_proficiency=11)
