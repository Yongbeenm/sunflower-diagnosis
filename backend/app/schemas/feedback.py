"""Feedback schemas."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class FeedbackStatus(str, Enum):
    """Feedback status values."""
    
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"


class FeedbackCreateRequest(BaseModel):
    """Request to create feedback."""
    
    subject: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=5000)
    contact_info: str | None = Field(default=None, max_length=255)  # Changed from contact
    diagnosis_session_id: str | None = Field(default=None)  # session_id sent from frontend


class FeedbackItem(BaseModel):
    """Feedback item response."""
    
    id: int
    subject: str
    message: str
    status: str  # Changed from FeedbackStatus enum to string to match frontend
    created_at: str  # Changed from datetime to string (ISO format)
    user_id: int | None  # Changed from submitted_by_id
    user_name: str | None  # Added for frontend display
    diagnosis_session_id: str | None
    media_url: str | None  # Added for frontend display


class FeedbackListResponse(BaseModel):
    """Paginated feedback list."""
    
    items: list[FeedbackItem]
    total: int
    page: int
    size: int


class FeedbackStatusUpdateRequest(BaseModel):
    """Request to update feedback status."""
    
    status: FeedbackStatus
