"""Pydantic schemas for AI endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# ============================================================================
# Chat Schemas
# ============================================================================

class AIChatRequest(BaseModel):
    """User chat message request."""
    
    message: str = Field(..., min_length=1, max_length=2000)
    locale: str = Field(default="en", pattern="^(en|km)$")
    conversation_id: str | None = None


class AIChatResponse(BaseModel):
    """AI chat response."""
    
    message: str
    conversation_id: str
    needs_diagnosis: bool = False
    extracted_symptoms: dict[str, Any] | None = None
    navigate_to: str | None = None
    action_type: str | None = None
    suggested_actions: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None


# ============================================================================
# Symptom Extraction Schemas
# ============================================================================

class SymptomExtractionRequest(BaseModel):
    """Request to extract symptoms from natural language."""
    
    message: str = Field(..., min_length=1, max_length=2000)
    locale: str = Field(default="en", pattern="^(en|km)$")


class ExtractedSymptom(BaseModel):
    """Structured symptom information extracted from text."""
    
    crop: str | None = None
    plant_part: list[str] = Field(default_factory=list)
    symptoms: list[str] = Field(default_factory=list)
    color_changes: list[str] = Field(default_factory=list)
    spots: list[str] = Field(default_factory=list)
    pests: list[str] = Field(default_factory=list)
    environment: list[str] = Field(default_factory=list)
    duration: str | None = None
    severity: str | list[str] | None = None  # Allow both string and list
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def model_post_init(self, __context) -> None:
        """Normalize severity to string if it's a list."""
        if isinstance(self.severity, list):
            # Join list items into a single string
            self.severity = ", ".join(self.severity) if self.severity else None


class SymptomExtractionResponse(BaseModel):
    """Response with extracted symptoms."""
    
    extracted: ExtractedSymptom
    mapped_symptom_ids: list[int] = Field(default_factory=list)
    unmapped_descriptions: list[str] = Field(default_factory=list)


# ============================================================================
# AI Diagnosis Schemas
# ============================================================================

class AIDiagnosisRequest(BaseModel):
    """Request for AI-assisted diagnosis."""
    
    message: str = Field(..., min_length=1, max_length=2000)
    locale: str = Field(default="en", pattern="^(en|km)$")
    image_base64: str | None = None


class AIDiagnosisResponse(BaseModel):
    """AI-assisted diagnosis response.
    
    This combines AI extraction with expert system diagnosis.
    """
    
    extracted_symptoms: ExtractedSymptom
    diagnosis_session_id: str | None = None
    expert_system_results: dict[str, Any]
    ai_explanation: str


# ============================================================================
# Image Analysis Schemas
# ============================================================================

class ImageAnalysisRequest(BaseModel):
    """Request for plant disease image analysis."""
    
    image_base64: str
    locale: str = Field(default="en", pattern="^(en|km)$")
    additional_context: str | None = None


class ImageObservation(BaseModel):
    """Structured observations from image analysis."""
    
    crop_identified: str | None = None
    crop_confidence: float | None = None
    plant_parts: list[str] = Field(default_factory=list)
    visible_symptoms: list[str] = Field(default_factory=list)
    color_abnormalities: list[str] = Field(default_factory=list)
    spots_lesions: list[str] = Field(default_factory=list)
    pests_visible: list[str] = Field(default_factory=list)
    image_quality: str | None = None
    possible_diseases: list[str] = Field(default_factory=list)


class ImageAnalysisResponse(BaseModel):
    """Image analysis response."""
    
    observations: ImageObservation
    analysis_text: str
    warning: str = "This is visual analysis only. Diagnosis requires expert system evaluation."


class ImageMatchDiseaseRequest(BaseModel):
    """Request to analyze image and match against system diseases."""
    
    image_base64: str
    locale: str = Field(default="en", pattern="^(en|km)$")
    additional_context: str | None = None


class MatchedDiseaseInfo(BaseModel):
    """A disease matched from the system database via image analysis."""
    
    disease_id: int
    slug: str
    name: str
    pathogen_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    image_url: str | None = None


class ImageMatchDiseaseResponse(BaseModel):
    """Response with matched disease from system database and auto-checked symptoms."""
    
    matched: bool = False
    disease: MatchedDiseaseInfo | None = None
    auto_checked_symptom_ids: list[int] = Field(default_factory=list)
    symptom_names: list[str] = Field(default_factory=list)
    observations: ImageObservation = Field(default_factory=ImageObservation)
    analysis_text: str = ""
    navigate_to: str | None = None
    warning: str = "This is AI visual analysis. Use the expert system to confirm."


# ============================================================================
# Admin/Expert Assistant Schemas
# ============================================================================

class DiseaseDraftRequest(BaseModel):
    """Request to generate disease knowledge draft."""
    
    description: str = Field(..., min_length=10, max_length=5000)
    locale: str = Field(default="en", pattern="^(en|km)$")
    image_base64: str | None = None


class DiseaseDraft(BaseModel):
    """AI-generated disease knowledge draft."""
    
    disease_name_en: str
    disease_name_km: str | None = None
    scientific_name: str | None = None
    pathogen_type: str | None = None
    description_en: str
    description_km: str | None = None
    symptoms: list[str] = Field(default_factory=list)
    causes: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    prevention: list[str] = Field(default_factory=list)
    treatment: list[str] = Field(default_factory=list)
    severity: str | None = None
    keywords: list[str] = Field(default_factory=list)
    related_diseases: list[str] = Field(default_factory=list)


class DiseaseDraftResponse(BaseModel):
    """Response with AI-generated disease draft."""
    
    draft: DiseaseDraft
    status: str = "draft"
    warning: str = "This is AI-generated content. Expert review and approval required."


class DuplicateCheckRequest(BaseModel):
    """Request to check for duplicate diseases."""
    
    disease_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    symptoms: list[str] = Field(default_factory=list)


class DuplicateMatch(BaseModel):
    """Potential duplicate disease match."""
    
    disease_id: int
    disease_name: str
    slug: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    reason: str


class DuplicateCheckResponse(BaseModel):
    """Response with potential duplicate matches."""
    
    is_likely_duplicate: bool
    matches: list[DuplicateMatch] = Field(default_factory=list)
    recommendation: str


# ============================================================================
# Health Check Schema
# ============================================================================

class AIHealthResponse(BaseModel):
    """AI service health status."""
    
    ollama_available: bool
    model_loaded: str | None = None
    vision_model_loaded: str | None = None
    status: str
    error: str | None = None
