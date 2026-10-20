from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AnalyzeRequest(StrictModel):
    opportunity_description: str = Field(min_length=20, max_length=20_000)
    company_name: str | None = Field(default=None, max_length=200)
    source_url: HttpUrl | None = None
    student_education: str = Field(min_length=1, max_length=4_000)
    student_skills: list[str] = Field(min_length=1, max_length=100)
    graduation_year: int | None = Field(default=None, ge=1900, le=2200)
    projects_or_experience: str | None = Field(default=None, max_length=8_000)
    daily_preparation_minutes: int | None = Field(default=None, ge=1, le=1_440)

    @field_validator("opportunity_description", "student_education")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be blank")
        return value.strip()

    @field_validator("company_name", "projects_or_experience")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None

    @field_validator("student_skills")
    @classmethod
    def normalize_skills(cls, value: list[str]) -> list[str]:
        skills = [skill.strip() for skill in value if skill.strip()]
        if not skills:
            raise ValueError("Provide at least one skill")
        return skills


class EligibilityStatus(str, Enum):
    MET = "Met"
    NOT_MET = "Not met"
    UNKNOWN = "Unknown"


class RequirementAssessment(StrictModel):
    requirement: str = Field(min_length=1)
    status: EligibilityStatus
    evidence: str = Field(min_length=1)


class DemonstratedSkill(StrictModel):
    skill: str = Field(min_length=1)
    evidence: str = Field(min_length=1)


class PotentialSkillGap(StrictModel):
    skill: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class PreparationAction(StrictModel):
    action: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class AnalysisReport(StrictModel):
    role_summary: str = Field(min_length=1)
    mandatory_requirements: list[RequirementAssessment]
    preferred_requirements: list[RequirementAssessment]
    demonstrated_skills: list[DemonstratedSkill]
    potential_skill_gaps: list[PotentialSkillGap]
    preparation_actions: list[PreparationAction]
    missing_or_ambiguous_details: list[str]
