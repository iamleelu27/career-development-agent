"""
career_agent.py
Workflow coordinator for Career Development Agent.

Orchestrates data loading, skill normalization, deterministic scoring,
role ranking, roadmap generation, and Markdown report generation.
Keeps business logic decoupled from Streamlit UI.
"""

from pathlib import Path
from typing import List, Optional
from data_loader import load_career_roles, get_sample_student
from models import CareerPlanReport, CareerRecommendation, CareerRole, StudentProfile
from recommendation_engine import rank_career_roles
from roadmap_engine import generate_learning_roadmap, generate_quick_start_plan


def generate_markdown_report(
    student: StudentProfile,
    primary_role: CareerRecommendation,
    alternative_roles: List[CareerRecommendation],
    quick_start: List[str],
    roadmap_months: list
) -> str:
    """
    Generate an educational, transparent Markdown career advising report.

    Strictly prohibits employment guarantees or fabricated achievements.
    Separates student-supplied evidence from analysis.
    """
    lines: List[str] = []

    lines.append(f"# Career Development Plan: {student.name}")
    lines.append(f"**Academic Background / Degree:** {student.degree}  ")
    lines.append(f"**Committed Weekly Learning Time:** {student.available_weekly_hours} hours/week  ")
    lines.append(f"**Target Learning Timeframe:** {student.learning_timeframe_months} months  \n")

    lines.append("---")
    lines.append("## 1. Evidence Supplied by Student")
    lines.append("### Current Skill Proficiencies (0 to 10 scale):")
    if student.skills:
        for skill, prof in student.skills.items():
            lines.append(f"- **{skill}:** {prof}/10")
    else:
        lines.append("- *No prior skills supplied.*")

    lines.append("\n### Interests:")
    if student.interests:
        for interest in student.interests:
            lines.append(f"- {interest}")
    else:
        lines.append("- *No specific interests supplied.*")

    lines.append("\n### Completed / Current Projects:")
    if student.existing_projects:
        for proj in student.existing_projects:
            lines.append(f"- {proj}")
    else:
        lines.append("- *No existing projects recorded.*")

    lines.append("\n### Existing Certifications:")
    if student.certifications:
        for cert in student.certifications:
            lines.append(f"- {cert}")
    else:
        lines.append("- *None recorded.*")

    lines.append("\n---")
    lines.append("## 2. Primary Recommended Career Role")
    lines.append(f"### **{primary_role.role_name}** (Match Score: **{primary_role.total_score}/100**)")
    lines.append(f"*{primary_role.description}*\n")

    b = primary_role.score_breakdown
    lines.append("### Score Breakdown (Deterministic 5-Factor Formula):")
    lines.append(f"- **Skill Match:** {b.skill_score}/50 pts")
    lines.append(f"- **Interest Match:** {b.interest_score}/20 pts")
    lines.append(f"- **Project Match:** {b.project_score}/15 pts")
    lines.append(f"- **Certification Match:** {b.certification_score}/10 pts")
    lines.append(f"- **Industry Alignment:** {b.industry_score}/5 pts")
    lines.append(f"- **Total Score:** **{b.total_score}/100 pts**\n")

    lines.append(f"**Recommendation Rationale:** {primary_role.explanation}\n")

    lines.append("### Skill Gap Analysis:")
    if primary_role.matched_skills:
        lines.append(f"- **Fully Matched Skills:** {', '.join(primary_role.matched_skills)}")
    if primary_role.partially_matched_skills:
        lines.append(f"- **Partially Matched Skills:** {', '.join(primary_role.partially_matched_skills)}")
    if primary_role.missing_skills:
        lines.append(f"- **Missing Skills to Build:** {', '.join(primary_role.missing_skills)}")

    lines.append("\n#### Prioritized Skill Gaps:")
    lines.append("| Skill | Current Gap | Priority Score (Gap × Importance) |")
    lines.append("| :--- | :---: | :---: |")
    for skill_name, gap, priority in primary_role.prioritized_gaps:
        lines.append(f"| {skill_name} | {gap} | {priority} |")

    lines.append("\n---")
    lines.append("## 3. Alternative Career Roles")
    for idx, alt in enumerate(alternative_roles, start=1):
        lines.append(f"### {idx}. {alt.role_name} — Score: {alt.total_score}/100")
        lines.append(f"- *{alt.description}*")
        lines.append(f"- **Rationale:** {alt.explanation}\n")

    lines.append("---")
    lines.append("## 4. Seven-Day Quick-Start Plan")
    for step in quick_start:
        lines.append(f"- {step}")

    lines.append(f"\n---")
    lines.append(f"## 5. {len(roadmap_months)}-Month Learning Roadmap")
    for rm in roadmap_months:
        lines.append(f"### Month {rm.month}: {rm.objective}")
        lines.append(f"- **Focus Skills:** {', '.join(rm.skills_to_study)}")
        lines.append(f"- **Estimated Time:** {rm.estimated_weekly_hours} hours/week")
        lines.append("- **Practical Exercises:**")
        for ex in rm.practical_exercises:
            lines.append(f"  - {ex}")
        lines.append(f"- **Observable Deliverable:** {rm.deliverable}")
        lines.append(f"- **Completion Criteria:** {rm.completion_criteria}\n")

    lines.append("---")
    lines.append("## 6. Recommended Hands-On Projects")
    for proj in primary_role.recommended_projects:
        lines.append(f"- **{proj}**")

    if primary_role.optional_certifications:
        lines.append("\n## 7. Optional Certifications (Study After Hands-On Projects)")
        for cert in primary_role.optional_certifications:
            lines.append(f"- {cert}")

    lines.append("\n---")
    lines.append("> **Important Advisory Disclaimer:** This recommendation is a personalized learning guide ")
    lines.append("> designed for educational planning. It does not constitute a guarantee of employment, hiring outcome, ")
    lines.append("> or job placement. Career progression depends on consistent individual practice, real-world portfolio ")
    lines.append("> development, and evolving industry standards.")

    return "\n".join(lines)


class CareerAgent:
    """
    High-level career advising coordinator.
    Encapsulates role catalog loading and student workflow execution.
    """

    def __init__(self, roles_path: Optional[Path] = None):
        self.roles_path = roles_path
        self.roles: List[CareerRole] = load_career_roles(self.roles_path)

    def load_sample_student(self, name: str = "Harsha") -> StudentProfile:
        """Load sample student profile from JSON."""
        return get_sample_student(name)

    def run_advising_workflow(self, student: StudentProfile) -> CareerPlanReport:
        """
        Execute full career advising workflow for a validated StudentProfile.

        Steps:
            1. Rank all career roles deterministically.
            2. Select primary role (top 1) and top 3 alternatives.
            3. Generate 7-day quick-start plan.
            4. Generate monthly learning roadmap.
            5. Assemble complete CareerPlanReport with Markdown export.

        Returns:
            Fully populated CareerPlanReport instance.
        """
        ranked_roles = rank_career_roles(self.roles, student)
        if not ranked_roles:
            raise ValueError("No career roles available for recommendation.")

        primary = ranked_roles[0]
        alternatives = ranked_roles[1:4]

        # Match primary CareerRole object for roadmap generator
        primary_role_obj = next(r for r in self.roles if r.role_name == primary.role_name)

        quick_start = generate_quick_start_plan(primary_role_obj, student)
        roadmap = generate_learning_roadmap(
            primary_role_obj,
            student,
            timeframe_months=student.learning_timeframe_months
        )

        md_report = generate_markdown_report(
            student=student,
            primary_role=primary,
            alternative_roles=alternatives,
            quick_start=quick_start,
            roadmap_months=roadmap
        )

        return CareerPlanReport(
            student_name=student.name,
            degree=student.degree,
            available_weekly_hours=student.available_weekly_hours,
            learning_timeframe_months=student.learning_timeframe_months,
            primary_role=primary,
            alternative_roles=alternatives,
            quick_start_plan=quick_start,
            roadmap=roadmap,
            recommended_projects=primary.recommended_projects,
            optional_certifications=primary.optional_certifications,
            markdown_report=md_report
        )
