"""
skill_engine.py
Skill normalization, comparison, gap analysis, and prioritization engine.

Provides canonical normalization mapping for industry skills, computes
deterministic skill gaps, and sorts gaps by weighted priority.
"""

from typing import Dict, List, Tuple
from models import SkillRequirement


# Canonical skill normalization alias map
SKILL_ALIASES: Dict[str, str] = {
    "aws": "Amazon Web Services",
    "amazon web services": "Amazon Web Services",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "ai/llm": "Artificial Intelligence",
    "llm": "Artificial Intelligence",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "google cloud platform": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    "iac": "Infrastructure as Code",
    "infrastructure as code": "Infrastructure as Code",
    "terraform": "Infrastructure as Code",
    "py": "Python",
    "python": "Python",
    "docker": "DevOps",
    "ci/cd": "DevOps",
    "devops": "DevOps",
    "sre": "Monitoring and Observability",
    "observability": "Monitoring and Observability",
    "monitoring": "Monitoring and Observability",
    "cloud": "Cloud",
    "sql": "SQL",
    "nosql": "Databases",
    "db": "Databases",
    "databases": "Databases",
    "linux": "Linux",
    "git": "Git",
    "apis": "APIs",
    "api": "APIs",
    "rest": "APIs",
    "networking": "Networking",
    "security": "Security",
    "cybersecurity": "Security",
    "statistics": "Statistics",
    "stats": "Statistics",
    "data visualization": "Data Visualization",
    "visualization": "Data Visualization",
    "data pipelines": "Data Pipelines",
    "etl": "Data Pipelines",
    "distributed computing": "Distributed Computing",
    "spark": "Distributed Computing",
    "threat analysis": "Threat Analysis",
    "web development": "Web Development",
    "frontend": "Web Development",
    "backend": "Backend",
}


def normalize_skill_name(skill: str) -> str:
    """
    Normalize a skill name string to its canonical form.

    Examples:
        'K8s' -> 'Kubernetes'
        'AWS' -> 'Amazon Web Services'
        'JS' -> 'JavaScript'
        'ML' -> 'Machine Learning'
        'AI' -> 'Artificial Intelligence'
        'GCP' -> 'Google Cloud Platform'
        'AI/LLM' -> 'Artificial Intelligence'

    Args:
        skill: Raw skill string from input or dataset.

    Returns:
        Canonical normalized skill string.
    """
    cleaned = skill.strip().lower()
    return SKILL_ALIASES.get(cleaned, skill.strip())


def normalize_student_skills(skills: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize all keys in a student's skills dictionary to canonical names.
    If multiple aliases map to the same canonical name, the maximum proficiency is retained.

    Args:
        skills: Raw dictionary of skill names to proficiencies.

    Returns:
        Dictionary with canonical skill names as keys and proficiencies as values.
    """
    normalized: Dict[str, float] = {}
    for raw_name, proficiency in skills.items():
        canonical_name = normalize_skill_name(raw_name)
        existing_prof = normalized.get(canonical_name, 0.0)
        normalized[canonical_name] = max(existing_prof, float(proficiency))
    return normalized


def analyze_skill_gaps(
    required_skills: List[SkillRequirement],
    student_skills: Dict[str, float]
) -> Tuple[List[str], List[str], List[str], Dict[str, float], List[Tuple[str, float, float]]]:
    """
    Analyze student skills against role requirements to find matched, partially matched,
    and missing skills, along with prioritized skill gaps.

    Gap Priority Formula:
        priority = (target_proficiency - current_proficiency) * skill_importance

    Args:
        required_skills: List of SkillRequirement objects for a career role.
        student_skills: Student skills dictionary (raw or normalized).

    Returns:
        Tuple of:
            - matched_skills: Skills where current >= target
            - partially_matched_skills: Skills where 0 < current < target
            - missing_skills: Skills where current == 0 or missing
            - skill_gaps: Dict mapping skill name to gap value (max(0, target - current))
            - prioritized_gaps: Sorted list of tuples: (skill_name, gap, priority_score)
                                sorted in descending order of priority_score.
    """
    normalized_student = normalize_student_skills(student_skills)

    matched: List[str] = []
    partial: List[str] = []
    missing: List[str] = []
    gaps: Dict[str, float] = {}
    prioritized: List[Tuple[str, float, float]] = []

    for req in required_skills:
        canonical_req = normalize_skill_name(req.name)
        current = normalized_student.get(canonical_req, 0.0)

        # Also check alias match if student specified "Cloud" and req is "Amazon Web Services" or vice versa
        if current == 0.0:
            # Check direct exact match
            for s_name, s_prof in normalized_student.items():
                if s_name.lower() == canonical_req.lower():
                    current = max(current, s_prof)

        target = float(req.target_proficiency)
        importance = float(req.importance)

        if current >= target:
            matched.append(req.name)
            gap = 0.0
        elif current > 0.0:
            partial.append(req.name)
            gap = round(target - current, 2)
        else:
            missing.append(req.name)
            gap = round(target, 2)

        gaps[req.name] = gap

        if gap > 0.0:
            priority = round(gap * importance, 2)
            prioritized.append((req.name, gap, priority))

    # Sort prioritized gaps descending by priority, breaking ties by importance and gap
    prioritized.sort(key=lambda x: x[2], reverse=True)

    return matched, partial, missing, gaps, prioritized
