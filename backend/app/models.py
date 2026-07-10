from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high"]
Level = Literal["pass", "warning", "fail"]
ExperimentType = Literal["hydraulic", "pneumatic", "circuit_design", "measurement"]


class Issue(BaseModel):
    category: str
    severity: Severity
    problem: str
    evidence: str
    suggestion: str
    confidence: float = Field(ge=0.0, le=1.0)


class KeyEvent(BaseModel):
    time_range: list[float] = Field(min_length=2, max_length=2)
    problem: str
    suggestion: str


class CheckReport(BaseModel):
    score: int = Field(ge=0, le=100)
    level: Level
    issues: list[Issue] = Field(default_factory=list)
    teacher_review_required: bool = False
    summary: str
    key_events: list[KeyEvent] | None = None


class TextCheckRequest(BaseModel):
    grade: str = "2024级本科"
    experiment_name: str = ""
    content: str
