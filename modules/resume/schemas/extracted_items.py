from typing import Optional
from pydantic import BaseModel, Field


class ResumeParserSchema(BaseModel):
    name : str = Field(..., description="Name of the candidate")
    email : str = Field(..., description="Email of the candidate")
    phone : str = Field(..., description="Phone number of the candidate")
    summary: str = Field(..., description="Summary of the candidate")
    education: list[dict] = Field(..., description="Education of the candidate")
    experience: list[dict] = Field(..., description="Experience of the candidate")
    skills: list[str] = Field(..., description="Skills of the candidate")
    projects: list[dict] = Field(..., description="Projects of the candidate")
    certifications: list[dict] = Field(..., description="Certifications of the candidate")
    achievements: list[dict] = Field(..., description="Achievements of the candidate")
    languages: list[str] = Field(..., description="Languages known by the candidate")

    # total fields
    total: int = 0