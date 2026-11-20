"""
tests/test_skill_engine.py
Tests for skill normalization, skill gap calculation, and gap prioritization.
"""

import pytest
from models import SkillRequirement
from skill_engine import (
    analyze_skill_gaps,
    normalize_skill_name,
    normalize_student_skills,
)


def test_skill_name_normalization():
    """Verify standard abbreviations normalize to canonical skill names."""
    assert normalize_skill_name("k8s") == "Kubernetes"
    assert normalize_skill_name("K8s") == "Kubernetes"
    assert normalize_skill_name("AWS") == "Amazon Web Services"
    assert normalize_skill_name("aws") == "Amazon Web Services"
    assert normalize_skill_name("JS") == "JavaScript"
    assert normalize_skill_name("ML") == "Machine Learning"
    assert normalize_skill_name("AI") == "Artificial Intelligence"
    assert normalize_skill_name("GCP") == "Google Cloud Platform"
    assert normalize_skill_name("ai/llm") == "Artificial Intelligence"


def test_normalize_student_skills_deduplication():
    """Verify alias deduplication keeps maximum proficiency value."""
    raw = {"AI": 4.0, "Artificial Intelligence": 6.0, "k8s": 3.0}
    normalized = normalize_student_skills(raw)
    assert normalized["Artificial Intelligence"] == 6.0
    assert normalized["Kubernetes"] == 3.0


def test_analyze_skill_gaps_classification():
    """Verify correct classification into matched, partially matched, and missing skills."""
    requirements = [
        SkillRequirement(name="Python", importance=5, target_proficiency=8),
        SkillRequirement(name="Kubernetes", importance=4, target_proficiency=7),
        SkillRequirement(name="Linux", importance=3, target_proficiency=6),
    ]

    student_skills = {
        "Python": 8.0,      # Current == target -> Matched
        "K8s": 4.0,         # Current < target -> Partial
        # Linux is not provided -> Missing
    }

    matched, partial, missing, gaps, prioritized = analyze_skill_gaps(requirements, student_skills)

    assert "Python" in matched
    assert "Kubernetes" in partial
    assert "Linux" in missing
    assert gaps["Python"] == 0.0
    assert gaps["Kubernetes"] == 3.0
    assert gaps["Linux"] == 6.0


def test_prioritized_gaps_ordering():
    """Verify prioritized gaps are sorted descending by (target - current) * importance."""
    requirements = [
        SkillRequirement(name="SkillA", importance=5, target_proficiency=8),  # gap=8, prio=40
        SkillRequirement(name="SkillB", importance=2, target_proficiency=6),  # gap=6, prio=12
        SkillRequirement(name="SkillC", importance=4, target_proficiency=7),  # gap=3 (prof=4), prio=12
    ]
    student_skills = {"SkillC": 4.0}

    _, _, _, _, prioritized = analyze_skill_gaps(requirements, student_skills)

    # First should be SkillA with priority 40.0
    assert prioritized[0][0] == "SkillA"
    assert prioritized[0][2] == 40.0
