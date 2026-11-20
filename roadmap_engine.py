"""
roadmap_engine.py
Prioritized career learning roadmap generator and 7-day quick-start planner.

Generates monthly learning objectives, practical exercises, measurable deliverables,
and completion criteria based on:
- Prioritized skill gaps: (target_proficiency - current_proficiency) * skill_importance
- Student's available weekly learning hours
- Requested learning timeframe (1 to 24 months)
"""

from typing import Dict, List, Optional, Tuple
from models import CareerRole, RoadmapMonth, StudentProfile
from skill_engine import analyze_skill_gaps, normalize_skill_name, normalize_student_skills


def generate_quick_start_plan(role: CareerRole, student: StudentProfile) -> List[str]:
    """
    Generate an actionable 7-day quick-start plan tailored to the top skill gaps.

    Args:
        role: Target career role.
        student: Student profile with current proficiencies.

    Returns:
        List of 7 daily actionable objectives.
    """
    _, _, _, _, prioritized = analyze_skill_gaps(role.required_skills, student.skills)
    top_skill = prioritized[0][0] if prioritized else (role.required_skills[0].name if role.required_skills else "Core Fundamentals")
    second_skill = prioritized[1][0] if len(prioritized) > 1 else (role.required_skills[1].name if len(role.required_skills) > 1 else "Systems Architecture")

    return [
        f"Day 1: Set up development environment, verify Python/Git tooling, and create the '{role.role_name.lower().replace(' ', '-')}-portfolio' repository.",
        f"Day 2: Audit baseline knowledge in {top_skill}; review canonical documentation and build a minimal 'Hello World' prototype.",
        f"Day 3: Write structured modular code focusing on {top_skill} fundamentals and establish Git branch protection and commit hygiene.",
        f"Day 4: Implement automated unit tests for {top_skill} modules with test assertions and edge case validation.",
        f"Day 5: Bridge {top_skill} with {second_skill} by designing a combined interface or containerized execution environment.",
        f"Day 6: Conduct peer code review or self-audit against industry conventions; package project with clear README documentation.",
        f"Day 7: Run end-to-end regression tests, measure baseline performance metrics, and lock in weekly study schedule for Month 1."
    ]


def generate_learning_roadmap(
    role: CareerRole,
    student: StudentProfile,
    timeframe_months: Optional[int] = None
) -> List[RoadmapMonth]:
    """
    Generate a monthly learning roadmap calibrated to the student's available weekly hours
    and prioritized skill gaps.

    Gap Priority Formula:
        priority = (target_proficiency - current_proficiency) * skill_importance

    Args:
        role: CareerRole instance.
        student: StudentProfile instance.
        timeframe_months: Optional override for duration (defaults to student's timeframe).

    Returns:
        List of RoadmapMonth objects covering each month in the timeframe.
    """
    months_count = timeframe_months or student.learning_timeframe_months
    months_count = max(1, min(24, months_count))

    weekly_hours = student.available_weekly_hours
    _, _, _, _, prioritized = analyze_skill_gaps(role.required_skills, student.skills)

    # Distribute prioritized skill gaps across the requested months
    # Map default learning sequence if available
    default_sequence = {m.month: m for m in role.learning_sequence}

    roadmap: List[RoadmapMonth] = []

    # Prepare prioritized skills queue
    priority_skill_names = [p[0] for p in prioritized]
    if not priority_skill_names:
        priority_skill_names = [r.name for r in role.required_skills]

    # Distribute skills across months
    for month_idx in range(1, months_count + 1):
        # Determine skills for this month
        chunk_size = max(1, len(priority_skill_names) // months_count)
        start_idx = (month_idx - 1) * chunk_size
        month_skills = priority_skill_names[start_idx : start_idx + chunk_size]
        if not month_skills and priority_skill_names:
            month_skills = [priority_skill_names[(month_idx - 1) % len(priority_skill_names)]]

        # Use curated sequence if available for this month index, else synthesize
        if month_idx in default_sequence:
            curated = default_sequence[month_idx]
            objective = curated.topic
            # Merge curated skills with student prioritized skills
            combined_skills = list(dict.fromkeys(month_skills + curated.skills))[:3]
            deliverable = curated.deliverable
            completion_criteria = curated.completion_criteria
            exercises = [
                f"Study architectural patterns and best practices for {', '.join(combined_skills)}.",
                f"Implement modular exercises dedicating {round(weekly_hours * 0.6, 1)} hrs/week to code authoring and testing.",
                f"Perform code reviews and document implementation tradeoffs ({round(weekly_hours * 0.4, 1)} hrs/week)."
            ]
        else:
            skills_str = ", ".join(month_skills)
            objective = f"Deep Dive into {skills_str} and Practical Application"
            deliverable = f"Production-ready tested module implementing {skills_str} patterns with full test suite."
            completion_criteria = (
                f"Unit test coverage >= 80%, zero critical linter warnings, "
                f"and verifiable execution under simulated workload."
            )
            exercises = [
                f"Build weekly hands-on laboratory exercises addressing gaps in {skills_str}.",
                f"Benchmark performance and profile resource utilization ({round(weekly_hours * 0.5, 1)} hrs/week).",
                f"Refactor for maintainability and author automated regression tests ({round(weekly_hours * 0.5, 1)} hrs/week)."
            ]
            combined_skills = month_skills

        roadmap.append(
            RoadmapMonth(
                month=month_idx,
                objective=objective,
                skills_to_study=combined_skills,
                practical_exercises=exercises,
                deliverable=deliverable,
                estimated_weekly_hours=weekly_hours,
                completion_criteria=completion_criteria
            )
        )

    return roadmap
