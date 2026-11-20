"""
tests/test_integration.py
End-to-end integration tests for CareerAgent workflow and report generation.
"""

import pytest
from career_agent import CareerAgent
from data_loader import load_career_roles, load_students


def test_data_loader_role_count():
    """Verify that exactly 10 technology roles are loaded from career_roles.json."""
    roles = load_career_roles()
    assert len(roles) == 10
    role_names = {r.role_name for r in roles}
    expected_roles = {
        "AI Platform Engineer",
        "Cloud Engineer",
        "DevOps Engineer",
        "Site Reliability Engineer",
        "Data Engineer",
        "Data Analyst",
        "Cybersecurity Analyst",
        "Full-Stack Developer",
        "Backend Developer",
        "Machine Learning Engineer"
    }
    assert role_names == expected_roles


def test_data_loader_student_profile():
    """Verify students.json contains Harsha's sample profile."""
    students = load_students()
    assert len(students) >= 1
    harsha = next(s for s in students if s.name == "Harsha")
    assert harsha.degree == "B.Tech Computer Science"
    assert harsha.skills["Python"] == 7.0
    assert harsha.available_weekly_hours == 8.0


def test_career_agent_workflow_execution():
    """Verify CareerAgent runs complete advising pipeline and generates report."""
    agent = CareerAgent()
    student = agent.load_sample_student("Harsha")
    report = agent.run_advising_workflow(student)

    # Primary role assertions
    assert report.primary_role.role_name == "AI Platform Engineer"
    assert report.primary_role.total_score > 50.0
    assert len(report.alternative_roles) == 3

    # Roadmap assertions
    assert len(report.roadmap) == 6
    assert len(report.quick_start_plan) == 7

    # Markdown report assertions
    md = report.markdown_report
    assert "# Career Development Plan: Harsha" in md
    assert "Evidence Supplied by Student" in md
    assert "Primary Recommended Career Role" in md
    assert "Alternative Career Roles" in md
    assert "Seven-Day Quick-Start Plan" in md
    assert "Learning Roadmap" in md
    assert "Important Advisory Disclaimer" in md
    assert "does not constitute a guarantee of employment" in md
