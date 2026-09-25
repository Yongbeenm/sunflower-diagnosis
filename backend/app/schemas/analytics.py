"""Pydantic schemas for agronomist and admin analytics."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DailyChecksTrend(BaseModel):
    """Daily diagnosis session count."""

    model_config = ConfigDict(frozen=True)

    date: str
    count: int


class TopSymptom(BaseModel):
    """Most frequently reported symptom."""

    model_config = ConfigDict(frozen=True)

    symptom_id: int
    code: str
    label: str
    count: int


class NoMatchPattern(BaseModel):
    """Symptom combination that resulted in a no_match diagnosis."""

    model_config = ConfigDict(frozen=True)

    symptoms: list[str]
    count: int


class AnalyticsOverviewResponse(BaseModel):
    """Dashboard metrics aggregate."""

    model_config = ConfigDict(frozen=True)

    checks_today: int
    checks_total: int
    checks_trend_30d: list[DailyChecksTrend]
    top_symptoms: list[TopSymptom]
    no_match_patterns: list[NoMatchPattern]
    pending_feedback_count: int
