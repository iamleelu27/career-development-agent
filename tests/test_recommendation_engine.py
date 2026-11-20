"""
tests/test_recommendation_engine.py
Tests for deterministic scoring, boundary guarantees, monotonicity, and Harsha ranking.
"""

import pytest
from data_loader import load_career_roles, get_sample_student
from models import CareerRole, SkillRequirement, StudentProfile
from recommendation_engine import rank_career_roles, score_role_for_student


@pytest.fixture
def sample_roles():
    """Load default 10 career roles from local JSON."""
    return load_career_roles()


@pytest.fixture
def harsha_profile():
    """Load standard Harsha sample profile from local JSON."""
    return get_sample_student("Harsha")


def test_scores_remain_between_zero_and_one_hundred(sample_roles):
    """Every career score must strictly remain within [0.0, 100.0]."""
    # Test zero profile
    zero_student = StudentProfile(
        name="Zero Student",
        degree="Literature",
        skills={},
        interests=[],
        existing_projects=[]
    )
    for role in sample_roles:
        rec = score_role_for_student(role, zero_student)
        assert 0.0 <= rec.total_score <= 100.0
        assert 0.0 <= rec.score_breakdown.skill_score <= 50.0

    # Test master profile with max skills
    master_skills = {r.name: 10.0 for role in sample_roles for r in role.required_skills}
    master_student = StudentProfile(
        name="Master Student",
        degree="Computer Science",
        skills=master_skills,
        interests=["Cloud", "Artificial Intelligence", "DevOps"],
        existing_projects=["Chatbot", "AI Platform"],
        certifications=["AWS Certified Solutions Architect - Associate", "CKA"]
    )
    for role in sample_roles:
        rec = score_role_for_student(role, master_student)
        assert 0.0 <= rec.total_score <= 100.0


def test_deterministic_scoring(sample_roles, harsha_profile):
    """Identical input profiles must always generate identical scores."""
    run1 = rank_career_roles(sample_roles, harsha_profile)
    run2 = rank_career_roles(sample_roles, harsha_profile)

    assert len(run1) == len(run2)
    for r1, r2 in zip(run1, run2):
        assert r1.role_name == r2.role_name
        assert r1.total_score == r2.total_score
        assert r1.score_breakdown.skill_score == r2.score_breakdown.skill_score


def test_monotonic_skill_improvement(sample_roles):
    """Increasing a relevant skill proficiency must improve or maintain the career score."""
    role = next(r for r in sample_roles if r.role_name == "AI Platform Engineer")

    student_low = StudentProfile(
        name="Harsha",
        degree="B.Tech Computer Science",
        skills={"Python": 7.0, "Cloud": 5.0, "Kubernetes": 3.0, "AI/LLM": 4.0},
        interests=["Cloud", "AI"],
        existing_projects=["Chatbot"]
    )

    student_high = StudentProfile(
        name="Harsha",
        degree="B.Tech Computer Science",
        skills={"Python": 7.0, "Cloud": 5.0, "Kubernetes": 6.0, "AI/LLM": 4.0},
        interests=["Cloud", "AI"],
        existing_projects=["Chatbot"]
    )

    rec_low = score_role_for_student(role, student_low)
    rec_high = score_role_for_student(role, student_high)

    assert rec_high.total_score > rec_low.total_score
    assert rec_high.score_breakdown.skill_score > rec_low.score_breakdown.skill_score
    # Kubernetes gap should decrease
    assert rec_high.skill_gaps["Kubernetes"] < rec_low.skill_gaps["Kubernetes"]


def test_harsha_sample_profile_top_recommendation(sample_roles, harsha_profile):
    """
    The Harsha sample profile must return 'AI Platform Engineer' among top recommendations
    based on the supplied local role data.
    """
    ranked = rank_career_roles(sample_roles, harsha_profile)
    top_three_names = [r.role_name for r in ranked[:3]]

    assert "AI Platform Engineer" in top_three_names
    # Primary recommendation
    assert ranked[0].role_name == "AI Platform Engineer"


def test_missing_skills_reported_correctly(sample_roles, harsha_profile):
    """Missing skills must be reported accurately for a recommended role."""
    ranked = rank_career_roles(sample_roles, harsha_profile)
    primary = ranked[0]
    # Harsha does not list Linux or MLOps initially
    assert "Linux" in primary.missing_skills or "MLOps" in primary.missing_skills
