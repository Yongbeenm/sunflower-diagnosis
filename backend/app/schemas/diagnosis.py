"""Schemas for diagnosis requests, results, evidence, and session history."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import DiagnosisAnswer, DiagnosisOutcome

AnswerType = Literal["yes", "no", "unknown"]


class SymptomAnswerItem(BaseModel):
    """Individual symptom answer entry."""

    symptom_id: int
    answer: AnswerType


class DiagnosisRequest(BaseModel):
    """Request payload for previewing or persisting a diagnosis session."""

    locale: str = "en"
    answers: dict[int, AnswerType] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_answers(cls, data: Any) -> Any:
        """Normalize answers whether provided as dict {id: answer} or list."""
        if isinstance(data, dict):
            # Check if symptoms/answers list was passed
            for list_key in ("symptoms", "answers"):
                items = data.get(list_key)
                if isinstance(items, list):
                    normalized: dict[int, str] = {}
                    for item in items:
                        if isinstance(item, dict) and "symptom_id" in item and "answer" in item:
                            normalized[int(item["symptom_id"])] = str(item["answer"])
                    data["answers"] = normalized
                    break
            # If answers is a dict with string integer keys, Pydantic automatically converts them
        return data


class DiseaseRef(BaseModel):
    """Reference to a disease candidate."""

    id: int | None = None
    slug: str
    name: str


class EvidenceSymptomDTO(BaseModel):
    """Symptom entry in an evidence group."""

    symptom: str
    weight: float


class EvidenceDTO(BaseModel):
    """Structured evidence for a candidate disease."""

    supporting: list[EvidenceSymptomDTO] = Field(default_factory=list)
    against: list[EvidenceSymptomDTO] = Field(default_factory=list)
    missing_key: list[EvidenceSymptomDTO] = Field(default_factory=list)


class DiagnosisResultDTO(BaseModel):
    """Ranked diagnosis candidate outcome."""

    rank: int
    disease: DiseaseRef
    score: float
    confidence: float
    evidence: EvidenceDTO


class NextQuestionDTO(BaseModel):
    """Suggested discriminating question."""

    symptom: str
    information_gain: float


class DiagnosisResponse(BaseModel):
    """Response payload for diagnosis session runs and previews."""

    session_id: uuid.UUID | None = None
    ruleset_version: str
    outcome: DiagnosisOutcome
    results: list[DiagnosisResultDTO] = Field(default_factory=list)
    next_best_questions: list[NextQuestionDTO] = Field(default_factory=list)
    feedback_prompt: str | None = None


class SelectedSymptomDTO(BaseModel):
    """Persisted user answer to a specific symptom."""

    symptom_id: int
    symptom_code: str
    answer: DiagnosisAnswer


class DiagnosisSessionSummaryDTO(BaseModel):
    """Summary item in a user's diagnosis history list."""

    id: uuid.UUID
    created_at: datetime
    locale: str
    symptom_count: int
    outcome: DiagnosisOutcome
    top_disease: DiseaseRef | None = None
    top_confidence: float | None = None

    model_config = ConfigDict(from_attributes=True)


class DiagnosisSessionListResponse(BaseModel):
    """Paginated list of user diagnosis sessions."""

    items: list[DiagnosisSessionSummaryDTO]
    total: int
    page: int
    size: int


class DiagnosisSessionDetailResponse(BaseModel):
    """Full detail of a saved diagnosis session."""

    session_id: uuid.UUID
    ruleset_version: str
    outcome: DiagnosisOutcome
    locale: str
    created_at: datetime
    symptom_count: int
    selected_symptoms: list[SelectedSymptomDTO] = Field(default_factory=list)
    results: list[DiagnosisResultDTO] = Field(default_factory=list)
    next_best_questions: list[NextQuestionDTO] = Field(default_factory=list)
    feedback_prompt: str | None = None
