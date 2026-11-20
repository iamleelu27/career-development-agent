"""
recommendation_engine.py
Deterministic 5-factor scoring and career recommendation engine.

Implements the official scoring weights:
- Skill Match: 50%
- Interest Match: 20%
- Project Match: 15%
- Certification Match: 10%
- Industry Match: 5%

Enforces bounds [0, 100], deterministic evaluation, and explainable breakdowns.
"""

import re
from typing import Dict, List, Set, Tuple
from models import (
    CareerRecommendation,
    CareerRole,
    ScoreBreakdown,
    StudentProfile,
)
from skill_engine import analyze_skill_gaps, normalize_skill_name, normalize_student_skills


# Weights for the 5-factor scoring model
WEIGHT_SKILL = 50.0
WEIGHT_INTEREST = 20.0
WEIGHT_PROJECT = 15.0
WEIGHT_CERTIFICATION = 10.0
WEIGHT_INDUSTRY = 5.0

TECH_DEGREE_KEYWORDS = {
    "computer", "software", "information", "technology", "cs", "it",
    "data", "engineering", "electrical", "electronics", "ai", "cloud"
}


def _tokenize(text: str) -> Set[str]:
    """Extract lowercased alphanumeric tokens of length >= 3."""
    return {w for w in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(w) >= 3}


def calculate_skill_score(
    role: CareerRole,
    student_skills: Dict[str, float]
) -> Tuple[float, List[str], List[str], List[str], Dict[str, float], List[Tuple[str, float, float]]]:
    """
    Calculate deterministic skill match score (0 to 50 points).

    Formula:
        skill_ratio = sum(weight_i * min(1.0, current_i / target_i)) / sum(weight_i)
        score = skill_ratio * 50.0

    Returns:
        Tuple of (skill_score, matched_skills, partially_matched_skills, missing_skills, gaps, prioritized_gaps)
    """
    matched, partial, missing, gaps, prioritized = analyze_skill_gaps(
        role.required_skills, student_skills
    )

    total_weight = sum(req.importance for req in role.required_skills)
    if total_weight == 0:
        return 0.0, matched, partial, missing, gaps, prioritized

    normalized_student = normalize_student_skills(student_skills)
    weighted_progress = 0.0

    for req in role.required_skills:
        canonical_req = normalize_skill_name(req.name)
        current = normalized_student.get(canonical_req, 0.0)

        # Fallback to case-insensitive match
        if current == 0.0:
            for s_name, s_prof in normalized_student.items():
                if s_name.lower() == canonical_req.lower():
                    current = max(current, s_prof)

        ratio = min(1.0, current / float(req.target_proficiency)) if req.target_proficiency > 0 else 0.0
        weighted_progress += float(req.importance) * ratio

    skill_ratio = weighted_progress / float(total_weight)
    skill_score = round(WEIGHT_SKILL * skill_ratio, 2)
    clamped_score = max(0.0, min(WEIGHT_SKILL, skill_score))

    return clamped_score, matched, partial, missing, gaps, prioritized


def calculate_interest_score(role: CareerRole, student_interests: List[str]) -> float:
    """
    Calculate deterministic interest match score (0 to 20 points).

    Matches student interests against role interests using canonical tokens and substrings.
    """
    if not student_interests or not role.interests:
        return 0.0

    role_interest_tokens: Set[str] = set()
    for ri in role.interests:
        role_interest_tokens.update(_tokenize(ri))
        canonical = normalize_skill_name(ri).lower()
        role_interest_tokens.add(canonical)

    matched_count = 0
    for si in student_interests:
        si_tokens = _tokenize(si)
        si_canonical = normalize_skill_name(si).lower()
        # Direct string equality or token overlap
        if si_canonical in role_interest_tokens or any(tok in role_interest_tokens for tok in si_tokens):
            matched_count += 1

    ratio = min(1.0, matched_count / max(1, len(student_interests)))
    score = round(WEIGHT_INTEREST * ratio, 2)
    return max(0.0, min(WEIGHT_INTEREST, score))


def calculate_project_score(role: CareerRole, existing_projects: List[str]) -> float:
    """
    Calculate deterministic project match score (0 to 15 points).

    Matches student's real completed projects against role domains and recommended projects.
    """
    if not existing_projects:
        return 0.0

    # Collect reference tokens from role description, skills, and recommended projects
    role_tokens: Set[str] = set()
    role_tokens.update(_tokenize(role.role_name))
    role_tokens.update(_tokenize(role.description))
    for p in role.recommended_projects:
        role_tokens.update(_tokenize(p))
    for s in role.required_skills:
        role_tokens.update(_tokenize(s.name))

    matched_projects = 0
    for proj in existing_projects:
        proj_tokens = _tokenize(proj)
        # Check if project tokens overlap with role domain tokens
        if proj_tokens.intersection(role_tokens):
            matched_projects += 1

    ratio = min(1.0, matched_projects / max(1, len(existing_projects)))
    score = round(WEIGHT_PROJECT * ratio, 2)
    return max(0.0, min(WEIGHT_PROJECT, score))


def calculate_certification_score(role: CareerRole, student_certs: List[str]) -> float:
    """
    Calculate deterministic certification match score (0 to 10 points).

    Matches student certifications with role optional certifications.
    """
    if not student_certs or not role.optional_certifications:
        return 0.0

    role_cert_tokens: Set[str] = set()
    for rc in role.optional_certifications:
        role_cert_tokens.update(_tokenize(rc))

    matched_certs = 0
    for sc in student_certs:
        sc_tokens = _tokenize(sc)
        if sc_tokens.intersection(role_cert_tokens):
            matched_certs += 1

    ratio = min(1.0, matched_certs / max(1, len(student_certs)))
    score = round(WEIGHT_CERTIFICATION * ratio, 2)
    return max(0.0, min(WEIGHT_CERTIFICATION, score))


def calculate_industry_score(role: CareerRole, student: StudentProfile) -> float:
    """
    Calculate deterministic industry match score (0 to 5 points).

    Evaluates student's stated industry preferences or degree alignment.
    """
    role_industry_tokens: Set[str] = set()
    for ind in role.industries:
        role_industry_tokens.update(_tokenize(ind))

    # If student provided preferred industries, score on those
    if student.preferred_industries:
        matched_industries = 0
        for pi in student.preferred_industries:
            pi_tokens = _tokenize(pi)
            if pi_tokens.intersection(role_industry_tokens):
                matched_industries += 1
        ratio = min(1.0, matched_industries / max(1, len(student.preferred_industries)))
        score = round(WEIGHT_INDUSTRY * ratio, 2)
        return max(0.0, min(WEIGHT_INDUSTRY, score))

    # Fallback to degree relevance check
    degree_tokens = _tokenize(student.degree)
    if degree_tokens.intersection(TECH_DEGREE_KEYWORDS):
        return WEIGHT_INDUSTRY

    return 0.0


def score_role_for_student(role: CareerRole, student: StudentProfile) -> CareerRecommendation:
    """
    Score a single career role for a student across all 5 dimensions.

    Returns:
        CareerRecommendation instance containing deterministic breakdown and explanation.
    """
    skill_score, matched, partial, missing, gaps, prioritized = calculate_skill_score(
        role, student.skills
    )
    interest_score = calculate_interest_score(role, student.interests)
    project_score = calculate_project_score(role, student.existing_projects)
    cert_score = calculate_certification_score(role, student.certifications)
    industry_score = calculate_industry_score(role, student)

    raw_total = skill_score + interest_score + project_score + cert_score + industry_score
    total_score = round(min(100.0, max(0.0, raw_total)), 2)

    breakdown = ScoreBreakdown(
        skill_score=skill_score,
        interest_score=interest_score,
        project_score=project_score,
        certification_score=cert_score,
        industry_score=industry_score,
        total_score=total_score
    )

    explanation = (
        f"{role.role_name} scored {total_score}/100. Breakdown: "
        f"Skill Match: {skill_score}/{int(WEIGHT_SKILL)} pts ({len(matched)} matched, {len(partial)} partial, {len(missing)} missing); "
        f"Interest Match: {interest_score}/{int(WEIGHT_INTEREST)} pts; "
        f"Project Match: {project_score}/{int(WEIGHT_PROJECT)} pts; "
        f"Certifications: {cert_score}/{int(WEIGHT_CERTIFICATION)} pts; "
        f"Industry Alignment: {industry_score}/{int(WEIGHT_INDUSTRY)} pts."
    )

    return CareerRecommendation(
        role_name=role.role_name,
        description=role.description,
        total_score=total_score,
        score_breakdown=breakdown,
        matched_skills=matched,
        partially_matched_skills=partial,
        missing_skills=missing,
        skill_gaps=gaps,
        prioritized_gaps=prioritized,
        explanation=explanation,
        optional_certifications=role.optional_certifications,
        recommended_projects=role.recommended_projects
    )


def rank_career_roles(
    roles: List[CareerRole],
    student: StudentProfile
) -> List[CareerRecommendation]:
    """
    Rank all available career roles for a student profile in descending order of total score.
    Ties are broken deterministically by skill_score and alphabetical role name.

    Returns:
        List of CareerRecommendation objects ranked from highest to lowest score.
    """
    recommendations = [score_role_for_student(role, student) for role in roles]
    recommendations.sort(
        key=lambda r: (r.total_score, r.score_breakdown.skill_score, r.role_name),
        reverse=True
    )
    return recommendations
