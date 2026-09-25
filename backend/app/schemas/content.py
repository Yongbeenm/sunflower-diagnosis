"""Schemas for content resources: diseases, symptoms, categories, translations, media."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import PathogenType

# ---------------------------------------------------------------------------
# Media Schemas
# ---------------------------------------------------------------------------


class MediaResponse(BaseModel):
    """Media upload result payload."""

    id: int
    url: str
    width: int | None = None
    height: int | None = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Symptom Category Schemas
# ---------------------------------------------------------------------------


class SymptomCategoryResponse(BaseModel):
    """Symptom category with localized label."""

    id: int
    code: str
    sort_order: int
    label: str

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Symptom Schemas
# ---------------------------------------------------------------------------


class SymptomItemResponse(BaseModel):
    """Symptom summary within category groupings."""

    id: int
    code: str
    label: str
    is_environmental: bool


class CategoryGroupedSymptoms(BaseModel):
    """Group of symptoms under a specific plant part category."""

    category: SymptomCategoryResponse
    symptoms: list[SymptomItemResponse] = Field(default_factory=list)


class SymptomDetailResponse(BaseModel):
    """Full detail of a symptom resource."""

    id: int
    code: str
    category_id: int
    is_environmental: bool
    label: str
    translations: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class SymptomCreateRequest(BaseModel):
    """Payload to create an observable symptom."""

    code: str
    category_id: int
    is_environmental: bool = False
    label_en: str
    label_km: str | None = None


class SymptomUpdateRequest(BaseModel):
    """Payload to update an existing symptom."""

    code: str | None = None
    category_id: int | None = None
    is_environmental: bool | None = None
    label_en: str | None = None
    label_km: str | None = None


# ---------------------------------------------------------------------------
# Disease Symptom & Weights Schemas
# ---------------------------------------------------------------------------


class DiseaseSymptomWeightItem(BaseModel):
    """Association weight and rule flags for a symptom on a disease."""

    symptom_id: int
    weight: float = Field(ge=0.0, le=1.0)
    is_required: bool = False
    is_pathognomonic: bool = False


class DiseaseSymptomsBulkUpdateRequest(BaseModel):
    """Payload to atomically replace all symptom weights for a disease."""

    symptoms: list[DiseaseSymptomWeightItem] = Field(default_factory=list)


class DiseaseSymptomGroupedItem(BaseModel):
    """Symptom weight details rendered inside grouped disease detail."""

    symptom_id: int
    code: str
    label: str
    weight: float
    is_required: bool
    is_pathognomonic: bool


class DiseaseSymptomCategoryGroup(BaseModel):
    """Grouped symptoms for a disease organized by category."""

    category: SymptomCategoryResponse
    symptoms: list[DiseaseSymptomGroupedItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Disease Schemas
# ---------------------------------------------------------------------------


class DiseaseListItemResponse(BaseModel):
    """Disease summary item for catalog and search results."""

    id: int
    slug: str
    pathogen_type: PathogenType
    is_published: bool
    image_url: str | None = None
    name: str
    description: str | None = None


class DiseaseListResponse(BaseModel):
    """Paginated list of disease catalog results."""

    items: list[DiseaseListItemResponse] = Field(default_factory=list)
    total: int
    page: int
    size: int


class DiseaseDetailResponse(BaseModel):
    """Comprehensive disease detail with localized content and grouped symptoms."""

    id: int
    slug: str
    pathogen_type: PathogenType
    is_published: bool
    image_url: str | None = None
    name: str
    description: str | None = None
    cause: str | None = None
    treatment: str | None = None
    prevention: str | None = None
    translations: dict[str, dict[str, str]] = Field(default_factory=dict)
    symptom_groups: list[DiseaseSymptomCategoryGroup] = Field(default_factory=list)


class DiseaseCreateRequest(BaseModel):
    """Payload to create a new disease record with initial English content."""

    slug: str
    pathogen_type: PathogenType
    image_media_id: int | None = None
    is_published: bool = False
    name_en: str
    description_en: str | None = None
    cause_en: str | None = None
    treatment_en: str | None = None
    prevention_en: str | None = None
    name_km: str | None = None
    description_km: str | None = None
    cause_km: str | None = None
    treatment_km: str | None = None
    prevention_km: str | None = None


class DiseaseUpdateRequest(BaseModel):
    """Payload to update disease attributes."""

    pathogen_type: PathogenType | None = None
    image_media_id: int | None = None
    media_id: int | None = None
    is_published: bool | None = None

    @model_validator(mode="after")
    def unify_media_id(self) -> DiseaseUpdateRequest:
        if self.image_media_id is None and self.media_id is not None:
            self.image_media_id = self.media_id
        return self


class DiseaseTranslationsUpdateRequest(BaseModel):
    """Payload to bulk upsert field translations for a specific locale."""

    fields: dict[str, str] = Field(default_factory=dict)
