"""
models.py
Data models and Pydantic validation schemas for Career Development Agent.

Defines schemas for Student Profiles, Career Roles, Skill Requirements,
Score Breakdowns, Recommendations, and Monthly Roadmaps.
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, field_validator


class SkillRequirement(BaseModel):
    """Defines a required skill for a career role."""
    name: str = Field(..., description="Canonical name of the skill")
    importance: int = Field(..., ge=1, le=5, description="Importance weight between 1 and 5")
    target_proficiency: int = Field(..., ge=1, le=10, description="Target beginner proficiency between 1 and 10")


class LearningSequenceMonth(BaseModel):
    """Template for a monthly learning milestone defined in career role catalog."""
    month: int = Field(..., ge=1, le=24, description="Month number")
    topic: str = Field(..., description="Focus topic or theme")
    skills: List[str] = Field(default_factory=list, description="Skills exercised in this month")
    deliverable: str = Field(..., description="Observable hands-on artifact or deliverable")
    completion_criteria: str = Field(..., description="Objective completion and verification criteria")


class CareerRole(BaseModel):
    """Defines a target technology career role."""
    role_name: str = Field(..., description="Name of the career role")
    description: str = Field(..., description="Overview and responsibilities of the role")
    interests: List[str] = Field(default_factory=list, description="Associated technical interests")
    industries: List[str] = Field(default_factory=list, description="Primary industry domains")
    required_skills: List[SkillRequirement] = Field(..., description="Required skills with weights and targets")
    optional_certifications: List[str] = Field(default_factory=list, description="Industry-recognized certifications")
    recommended_projects: List[str] = Field(default_factory=list, description="Hands-on portfolio project ideas")
    learning_sequence: List[LearningSequenceMonth] = Field(default_factory=list, description="Structured roadmap")


class StudentProfile(BaseModel):
    """
    Validated student input profile.
    Strictly enforces proficiency ranges (0-10) and learning timeframe (1-24 months).
    """
    name: str = Field(..., min_length=1, description="Student full name")
    degree: str = Field(..., min_length=1, description="Degree or academic background")
    skills: Dict[str, float] = Field(default_factory=dict, description="Skill proficiencies keyed by skill name")
    interests: List[str] = Field(default_factory=list, description="Technical interest tags")
    existing_projects: List[str] = Field(default_factory=list, description="Completed or current hands-on projects")
    certifications: List[str] = Field(default_factory=list, description="Current earned certifications")
    preferred_industries: List[str] = Field(default_factory=list, description="Preferred industries")
    available_weekly_hours: float = Field(
        default=8.0,
        ge=1.0,
        le=80.0,
        description="Available learning hours per week (1 to 80)"
    )
    learning_timeframe_months: int = Field(
        default=6,
        ge=1,
        le=24,
        description="Requested learning timeframe in months (1 to 24)"
    )

    @field_validator("skills")
    @classmethod
    def validate_skills_proficiency(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate that each skill proficiency value is between 0.0 and 10.0."""
        for skill_name, prof in v.items():
            if prof < 0.0 or prof > 10.0:
                raise ValueError(
                    f"Proficiency for skill '{skill_name}' must be between 0 and 10. Received: {prof}"
                )
        return v


class ScoreBreakdown(BaseModel):
    """Deterministic score breakdown according to the 5-factor scoring model."""
    skill_score: float = Field(..., ge=0.0, le=50.0, description="Skill match contribution (max 50%)")
    interest_score: float = Field(..., ge=0.0, le=20.0, description="Interest match contribution (max 20%)")
    project_score: float = Field(..., ge=0.0, le=15.0, description="Project match contribution (max 15%)")
    certification_score: float = Field(..., ge=0.0, le=10.0, description="Certification contribution (max 10%)")
    industry_score: float = Field(..., ge=0.0, le=5.0, description="Industry match contribution (max 5%)")
    total_score: float = Field(..., ge=0.0, le=100.0, description="Total score out of 100")


class CareerRecommendation(BaseModel):
    """Recommendation result for a specific career role."""
    role_name: str
    description: str
    total_score: float = Field(..., ge=0.0, le=100.0)
    score_breakdown: ScoreBreakdown
    matched_skills: List[str] = Field(default_factory=list)
    partially_matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    skill_gaps: Dict[str, float] = Field(default_factory=dict)
    prioritized_gaps: List[Tuple[str, float, float]] = Field(default_factory=list)
    explanation: str
    optional_certifications: List[str] = Field(default_factory=list)
    recommended_projects: List[str] = Field(default_factory=list)


class RoadmapMonth(BaseModel):
    """Concrete monthly roadmap step customized for a student."""
    month: int
    objective: str
    skills_to_study: List[str]
    practical_exercises: List[str]
    deliverable: str
    estimated_weekly_hours: float
    completion_criteria: str


class CareerPlanReport(BaseModel):
    """Complete career advising plan report."""
    student_name: str
    degree: str
    available_weekly_hours: float
    learning_timeframe_months: int
    primary_role: CareerRecommendation
    alternative_roles: List[CareerRecommendation]
    quick_start_plan: List[str]
    roadmap: List[RoadmapMonth]
    recommended_projects: List[str]
    optional_certifications: List[str]
    markdown_report: str
