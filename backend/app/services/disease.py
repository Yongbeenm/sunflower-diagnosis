"""Disease service orchestrating CRUD, full-text search, and atomic symptom weights."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import ConflictError, NotFoundError, ValidationFailedError
from app.models.auth import User
from app.models.disease import Disease
from app.models.enums import PathogenType
from app.repositories.disease import DiseaseRepository
from app.repositories.symptom import SymptomRepository
from app.schemas.content import (
    DiseaseCreateRequest,
    DiseaseDetailResponse,
    DiseaseListItemResponse,
    DiseaseListResponse,
    DiseaseSymptomCategoryGroup,
    DiseaseSymptomGroupedItem,
    DiseaseSymptomsBulkUpdateRequest,
    DiseaseTranslationsUpdateRequest,
    DiseaseUpdateRequest,
    SymptomCategoryResponse,
)
from app.services.audit import AuditService
from app.services.media.storage import LocalDiskBackend, MediaBackend, S3MediaBackend


class DiseaseService:
    """Business operations for sunflower diseases, bulk symptoms, and localized content."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = DiseaseRepository(session)
        self.symptom_repo = SymptomRepository(session)
        self.audit = AuditService(session)
        self.settings = get_settings()
        self.media_backend: MediaBackend = self._get_media_backend()

    def _get_media_backend(self) -> MediaBackend:
        if self.settings.MEDIA_BACKEND == "s3":
            return S3MediaBackend(
                bucket_name="sunflower-media",
                region="ap-southeast-1",
                public_cdn_url=self.settings.MEDIA_PUBLIC_URL,
            )
        return LocalDiskBackend(
            root_dir=self.settings.MEDIA_ROOT,
            public_base_url=self.settings.MEDIA_PUBLIC_URL,
        )

    async def list_diseases(
        self,
        q: str | None = None,
        category: str | None = None,
        pathogen: PathogenType | None = None,
        published: bool | None = None,
        page: int = 1,
        size: int = 20,
        locale: str = "en",
    ) -> DiseaseListResponse:
        """List diseases matching filters and full-text search queries with localized summaries."""
        diseases, total = await self.repository.list_diseases(
            q=q,
            category=category,
            pathogen=pathogen,
            published=published,
            page=page,
            size=size,
        )

        disease_ids = [d.id for d in diseases]
        trans_map = await self.repository.get_translations_for_diseases(disease_ids, locale=locale)

        items: list[DiseaseListItemResponse] = []
        for d in diseases:
            t = trans_map.get(d.id, {})
            name = t.get("name", d.slug.replace("-", " ").title())
            desc = t.get("description")

            image_url = None
            if d.image_media:
                image_url = await self.media_backend.get_url(d.image_media.storage_key)

            items.append(
                DiseaseListItemResponse(
                    id=d.id,
                    slug=d.slug,
                    pathogen_type=d.pathogen_type,
                    is_published=d.is_published,
                    image_url=image_url,
                    name=name,
                    description=desc,
                )
            )

        return DiseaseListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
        )

    async def get_disease(self, slug: str, locale: str = "en") -> DiseaseDetailResponse:
        """Fetch disease detail with per-field fallback to English and grouped symptom weights."""
        disease = await self.repository.get_by_slug(slug)
        if not disease:
            raise NotFoundError(detail=f"Disease with slug '{slug}' not found")

        trans_map = await self.repository.get_translations_for_diseases([disease.id], locale=locale)
        t = trans_map.get(disease.id, {})

        # Load all translations for inspection
        all_trans = await self.repository.get_all_disease_translations(disease.id)

        # Per-field fallback
        name = t.get("name", disease.slug.replace("-", " ").title())
        description = t.get("description")
        cause = t.get("cause")
        treatment = t.get("treatment")
        prevention = t.get("prevention")

        image_url = None
        if disease.image_media:
            image_url = await self.media_backend.get_url(disease.image_media.storage_key)

        # Symptoms grouped by plant part category
        categories = await self.symptom_repo.list_categories()
        cat_labels = await self.symptom_repo.get_category_translations(locale=locale)
        sym_labels = await self.symptom_repo.get_symptom_translations(locale=locale)

        grouped_map: dict[int, list[DiseaseSymptomGroupedItem]] = {c.id: [] for c in categories}
        for ds in disease.disease_symptoms:
            symptom = ds.symptom
            if not symptom:
                continue
            item = DiseaseSymptomGroupedItem(
                symptom_id=symptom.id,
                code=symptom.code,
                label=sym_labels.get(symptom.id, symptom.code.replace("_", " ").title()),
                weight=float(ds.weight),
                is_required=ds.is_required,
                is_pathognomonic=ds.is_pathognomonic,
            )
            grouped_map.setdefault(symptom.category_id, []).append(item)

        symptom_groups: list[DiseaseSymptomCategoryGroup] = []
        for c in categories:
            items_in_cat = grouped_map.get(c.id, [])
            if items_in_cat:
                items_in_cat.sort(key=lambda i: (-i.weight, i.label.lower()))
                symptom_groups.append(
                    DiseaseSymptomCategoryGroup(
                        category=SymptomCategoryResponse(
                            id=c.id,
                            code=c.code,
                            sort_order=c.sort_order,
                            label=cat_labels.get(c.id, c.code.replace("_", " ").title()),
                        ),
                        symptoms=items_in_cat,
                    )
                )

        return DiseaseDetailResponse(
            id=disease.id,
            slug=disease.slug,
            pathogen_type=disease.pathogen_type,
            is_published=disease.is_published,
            image_url=image_url,
            name=name,
            description=description,
            cause=cause,
            treatment=treatment,
            prevention=prevention,
            translations=all_trans,
            symptom_groups=symptom_groups,
        )

    async def create_disease(self, req: DiseaseCreateRequest, user: User) -> DiseaseDetailResponse:
        """Create a disease record with initial translations and audit trail."""
        existing = await self.repository.get_by_slug_simple(req.slug)
        if existing:
            raise ConflictError(detail=f"Disease with slug '{req.slug}' already exists")

        disease = Disease(
            slug=req.slug,
            pathogen_type=req.pathogen_type,
            image_media_id=req.image_media_id,
            is_published=req.is_published,
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        await self.repository.create(disease)

        # English translations
        en_fields = {
            "name": req.name_en,
            "description": req.description_en,
            "cause": req.cause_en,
            "treatment": req.treatment_en,
            "prevention": req.prevention_en,
        }
        for field, val in en_fields.items():
            if val:
                await self.repository.set_translation(disease.id, "en", field, val)

        # Khmer translations
        km_fields = {
            "name": req.name_km,
            "description": req.description_km,
            "cause": req.cause_km,
            "treatment": req.treatment_km,
            "prevention": req.prevention_km,
        }
        for field, val in km_fields.items():
            if val:
                await self.repository.set_translation(disease.id, "km", field, val)

        await self.audit.record(
            actor_id=user.id,
            action="create",
            entity_type="disease",
            entity_id=disease.id,
            diff={"slug": req.slug, "pathogen_type": req.pathogen_type, "name_en": req.name_en},
        )

        return await self.get_disease(disease.slug, locale="en")

    async def update_disease(
        self,
        disease_id: int,
        req: DiseaseUpdateRequest,
        user: User,
    ) -> DiseaseDetailResponse:
        """Update disease metadata with audit trail."""
        disease = await self.repository.get_by_id(disease_id)
        if not disease:
            raise NotFoundError(detail=f"Disease with ID {disease_id} not found")

        diff: dict[str, Any] = {}

        if req.pathogen_type is not None and req.pathogen_type != disease.pathogen_type:
            diff["pathogen_type"] = {"old": disease.pathogen_type, "new": req.pathogen_type}
            disease.pathogen_type = req.pathogen_type

        if req.image_media_id is not None and req.image_media_id != disease.image_media_id:
            diff["image_media_id"] = {"old": disease.image_media_id, "new": req.image_media_id}
            disease.image_media_id = req.image_media_id

        if req.is_published is not None and req.is_published != disease.is_published:
            diff["is_published"] = {"old": disease.is_published, "new": req.is_published}
            disease.is_published = req.is_published

        user_id = user.id
        disease_id = disease.id
        disease_slug = disease.slug

        disease.updated_by_id = user_id
        await self.session.flush()

        if diff:
            await self.audit.record(
                actor_id=user_id,
                action="update",
                entity_type="disease",
                entity_id=disease_id,
                diff=diff,
            )

        if "image_media_id" in diff:
            self.session.expire(disease, ["image_media"])

        return await self.get_disease(disease_slug, locale="en")

    async def delete_disease(self, disease_id: int, user: User) -> None:
        """Permanently delete a disease from the database."""
        disease = await self.repository.get_by_id(disease_id)
        if not disease:
            raise NotFoundError(detail=f"Disease with ID {disease_id} not found")

        # Record audit before deletion
        await self.audit.record(
            actor_id=user.id,
            action="delete",
            entity_type="disease",
            entity_id=disease.id,
            diff={"deleted": True, "name": disease.slug},
        )

        # Delete the disease record
        await self.session.delete(disease)
        await self.session.flush()

    async def replace_symptoms(
        self,
        disease_id: int,
        req: DiseaseSymptomsBulkUpdateRequest,
        user: User,
    ) -> DiseaseDetailResponse:
        """Atomically replace all symptom weights for a disease in one single transaction.

        Validates all symptom IDs exist. Rejects with HTTP 422 naming the bad index
        if any are unknown.
        """
        disease = await self.repository.get_by_id(disease_id)
        if not disease:
            raise NotFoundError(detail=f"Disease with ID {disease_id} not found")

        # 1. Validate all symptom IDs exist
        requested_ids = [item.symptom_id for item in req.symptoms]
        existing_ids = await self.repository.get_symptom_ids(requested_ids)

        errors: list[dict[str, Any]] = []
        for idx, item in enumerate(req.symptoms):
            if item.symptom_id not in existing_ids:
                errors.append(
                    {
                        "field": f"symptoms[{idx}].symptom_id",
                        "message": f"Symptom ID {item.symptom_id} does not exist",
                    }
                )

        if errors:
            raise ValidationFailedError(
                detail="One or more symptom IDs in the bulk update are invalid",
                errors=errors,
            )

        # 2. Atomic replacement in one transaction
        weights_tuple = [
            (item.symptom_id, item.weight, item.is_required, item.is_pathognomonic)
            for item in req.symptoms
        ]
        await self.repository.bulk_replace_symptoms(disease_id, weights_tuple)

        disease.updated_by_id = user.id
        await self.session.flush()

        # 3. Audit trail
        await self.audit.record(
            actor_id=user.id,
            action="bulk_update_symptoms",
            entity_type="disease",
            entity_id=disease.id,
            diff={"symptom_count": len(req.symptoms)},
        )

        return await self.get_disease(disease.slug, locale="en")

    async def update_translations(
        self,
        disease_id: int,
        locale: str,
        req: DiseaseTranslationsUpdateRequest,
        user: User,
    ) -> DiseaseDetailResponse:
        """Upsert translations for disease fields in a specific locale."""
        disease = await self.repository.get_by_id(disease_id)
        if not disease:
            raise NotFoundError(detail=f"Disease with ID {disease_id} not found")

        for field, value in req.fields.items():
            await self.repository.set_translation(disease.id, locale, field, value)

        disease.updated_by_id = user.id
        await self.session.flush()

        await self.audit.record(
            actor_id=user.id,
            action="update_translations",
            entity_type="disease",
            entity_id=disease.id,
            diff={"locale": locale, "fields": list(req.fields.keys())},
        )

        return await self.get_disease(disease.slug, locale=locale)
