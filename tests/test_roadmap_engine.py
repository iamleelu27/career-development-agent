"""
tests/test_roadmap_engine.py
Tests for roadmap length, weekly hours calibration, quick-start plans, and deliverables.
"""

import pytest
from data_loader import load_career_roles, get_sample_student
from roadmap_engine import generate_learning_roadmap, generate_quick_start_plan


@pytest.fixture
def sample_role():
    """Get the primary AI Platform Engineer role."""
    roles = load_career_roles()
    return next(r for r in roles if r.role_name == "AI Platform Engineer")


@pytest.fixture
def harsha_profile():
    """Load standard Harsha student profile."""
    return get_sample_student("Harsha")


def test_roadmap_length_matches_requested_timeframe(sample_role, harsha_profile):
    """Generated roadmap length must exactly equal the requested timeframe in months."""
    for requested_months in [1, 3, 6, 12]:
        roadmap = generate_learning_roadmap(
            sample_role,
            harsha_profile,
            timeframe_months=requested_months
        )
        assert len(roadmap) == requested_months
        assert roadmap[0].month == 1
        assert roadmap[-1].month == requested_months


def test_roadmap_respects_weekly_learning_hours(sample_role, harsha_profile):
    """Roadmap must reflect student's available weekly hours."""
    harsha_profile.available_weekly_hours = 12.0
    roadmap = generate_learning_roadmap(sample_role, harsha_profile, timeframe_months=6)

    for month_step in roadmap:
        assert month_step.estimated_weekly_hours == 12.0


def test_roadmap_deliverables_and_completion_criteria(sample_role, harsha_profile):
    """Every month must have at least one observable deliverable and clear completion criteria."""
    roadmap = generate_learning_roadmap(sample_role, harsha_profile, timeframe_months=6)

    for step in roadmap:
        assert len(step.deliverable.strip()) > 10
        assert len(step.completion_criteria.strip()) > 10
        assert len(step.practical_exercises) >= 1
        assert len(step.skills_to_study) >= 1


def test_quick_start_plan_seven_days(sample_role, harsha_profile):
    """The quick start plan must contain exactly 7 actionable daily steps."""
    plan = generate_quick_start_plan(sample_role, harsha_profile)
    assert len(plan) == 7
    for day_num, day_text in enumerate(plan, start=1):
        assert f"Day {day_num}:" in day_text
