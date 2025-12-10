"""Pydantic schemas for structured LLM output."""
from pydantic import BaseModel, Field
from typing import List, Optional


class SkillMatch(BaseModel):
    """Individual skill match with evidence."""
    skill: str = Field(..., description="The skill name")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Match score between 0 and 1")
    evidence: str = Field(..., description="Quote or evidence from resume")
    relevance: str = Field(..., description="Explanation of relevance")


class ExperienceMatch(BaseModel):
    """Work experience match."""
    role: str = Field(..., description="Job role or position")
    years_experience: Optional[float] = Field(None, description="Years of experience")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Match score")
    evidence: str = Field(..., description="Relevant experience description from resume")


class EducationMatch(BaseModel):
    """Education qualification match."""
    degree: str = Field(..., description="Degree or certification")
    field: Optional[str] = Field(None, description="Field of study")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Match score")
    evidence: str = Field(..., description="Education details from resume")


class ResumeAnalysisReport(BaseModel):
    """Complete structured analysis report."""
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall match score")
    candidate_name: str = Field(..., description="Candidate name from resume")
    summary: str = Field(..., description="Executive summary of the match")
    strengths: List[str] = Field(..., description="Key strengths and matches")
    weaknesses: List[str] = Field(..., description="Gaps or weaknesses")
    skill_matches: List[SkillMatch] = Field(..., description="Detailed skill matches")
    experience_matches: List[ExperienceMatch] = Field(..., description="Experience matches")
    education_matches: List[EducationMatch] = Field(..., description="Education matches")
    recommendation: str = Field(..., description="Hiring recommendation")
    reasoning: str = Field(..., description="Detailed reasoning for the recommendation")
    
    # Additional metadata (optional, not in LLM response)
    resume_id: Optional[str] = None
    filename: Optional[str] = None

