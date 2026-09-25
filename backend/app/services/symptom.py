"""Symptom service implementing business logic and conflict guards."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError, ValidationFailedError
from app.models.auth import User
from app.models.symptom import Symptom
from app.repositories.symptom import SymptomRepository
from app.schemas.content import (
    CategoryGroupedSymptoms,
    SymptomCategoryResponse,
    SymptomCreateRequest,
    SymptomDetailResponse,
    SymptomItemResponse,
    SymptomUpdateRequest,
)
from app.services.audit import AuditService


class SymptomService:
    """Coordinates symptom resources, grouping, and referential integrity guards."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = SymptomRepository(session)
        self.audit = AuditService(session)

    async def list_categories(self, locale: str = "en") -> list[SymptomCategoryResponse]:
        """List symptom categories ordered by sort_order with localized labels."""
        categories = await self.repository.list_categories()
        cat_labels = await self.repository.get_category_translations(locale=locale)

        return [
            SymptomCategoryResponse(
                id=c.id,
                code=c.code,
                sort_order=c.sort_order,
                label=cat_labels.get(c.id, c.code.replace("_", " ").title()),
            )
            for c in categories
        ]

    async def get_grouped_symptoms(
        self,
        category_code: str | None = None,
        locale: str = "en",
    ) -> list[CategoryGroupedSymptoms]:
        """Fetch symptoms grouped by category, ordered by category sort_order then label.

        Single response feeding the symptom checker.
        """
        categories = await self.repository.list_categories()
        cat_labels = await self.repository.get_category_translations(locale=locale)
        symptoms = await self.repository.list_symptoms(category_code=category_code)
        sym_labels = await self.repository.get_symptom_translations(locale=locale)

        # Index symptoms by category_id
        grouped: dict[int, list[SymptomItemResponse]] = {c.id: [] for c in categories}
        for s in symptoms:
            label = sym_labels.get(s.id, s.code.replace("_", " ").title())
            grouped.setdefault(s.category_id, []).append(
                SymptomItemResponse(
                    id=s.id,
                    code=s.code,
                    label=label,
                    is_environmental=s.is_environmental,
                )
            )

        result: list[CategoryGroupedSymptoms] = []
        for c in categories:
            if category_code and c.code != category_code:
                continue
            cat_symptoms = grouped.get(c.id, [])
            # Sort symptoms alphabetically by localized label
            cat_symptoms.sort(key=lambda item: item.label.lower())

            result.append(
                CategoryGroupedSymptoms(
                    category=SymptomCategoryResponse(
                        id=c.id,
                        code=c.code,
                        sort_order=c.sort_order,
                        label=cat_labels.get(c.id, c.code.replace("_", " ").title()),
                    ),
                    symptoms=cat_symptoms,
                )
            )

        return result

    async def get_symptom(self, symptom_id: int, locale: str = "en") -> SymptomDetailResponse:
        """Fetch detail of an individual symptom."""
        symptom = await self.repository.get_by_id(symptom_id)
        if not symptom:
            raise NotFoundError(detail=f"Symptom with ID {symptom_id} not found")

        sym_labels = await self.repository.get_symptom_translations(locale=locale)
        all_trans = await self.repository.get_symptom_all_translations(symptom_id)

        return SymptomDetailResponse(
            id=symptom.id,
            code=symptom.code,
            category_id=symptom.category_id,
            is_environmental=symptom.is_environmental,
            label=sym_labels.get(symptom.id, symptom.code.replace("_", " ").title()),
            translations=all_trans,
        )

    async def create_symptom(
        self,
        req: SymptomCreateRequest,
        user: User,
    ) -> SymptomDetailResponse:
        """Create a new symptom with validation, translations, and audit log."""
        existing = await self.repository.get_by_code(req.code)
        if existing:
            raise ConflictError(detail=f"Symptom code '{req.code}' is already in use")

        category = await self.repository.get_category_by_id(req.category_id)
        if not category:
            raise ValidationFailedError(
                detail="Invalid category ID",
                errors=[
                    {"field": "category_id", "message": f"Category {req.category_id} not found"}
                ],
            )

        symptom = Symptom(
            code=req.code,
            category_id=req.category_id,
            is_environmental=req.is_environmental,
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        await self.repository.create(symptom)

        # Upsert labels
        await self.repository.set_translation(symptom.id, "en", req.label_en)
        if req.label_km:
            await self.repository.set_translation(symptom.id, "km", req.label_km)

        # Audit trail
        await self.audit.record(
            actor_id=user.id,
            action="create",
            entity_type="symptom",
            entity_id=symptom.id,
            diff={"code": req.code, "category_id": req.category_id, "label_en": req.label_en},
        )

        return await self.get_symptom(symptom.id, locale="en")

    async def update_symptom(
        self,
        symptom_id: int,
        req: SymptomUpdateRequest,
        user: User,
    ) -> SymptomDetailResponse:
        """Update symptom attributes with audit logging."""
        symptom = await self.repository.get_by_id(symptom_id)
        if not symptom:
            raise NotFoundError(detail=f"Symptom with ID {symptom_id} not found")

        diff: dict[str, Any] = {}

        if req.code is not None and req.code != symptom.code:
            existing = await self.repository.get_by_code(req.code)
            if existing and existing.id != symptom.id:
                raise ConflictError(detail=f"Symptom code '{req.code}' is already in use")
            diff["code"] = {"old": symptom.code, "new": req.code}
            symptom.code = req.code

        if req.category_id is not None and req.category_id != symptom.category_id:
            category = await self.repository.get_category_by_id(req.category_id)
            if not category:
                raise ValidationFailedError(
                    detail="Invalid category ID",
                    errors=[
                        {"field": "category_id", "message": f"Category {req.category_id} not found"}
                    ],
                )
            diff["category_id"] = {"old": symptom.category_id, "new": req.category_id}
            symptom.category_id = req.category_id

        if req.is_environmental is not None and req.is_environmental != symptom.is_environmental:
            diff["is_environmental"] = {
                "old": symptom.is_environmental,
                "new": req.is_environmental,
            }
            symptom.is_environmental = req.is_environmental

        symptom.updated_by_id = user.id

        if req.label_en is not None:
            await self.repository.set_translation(symptom.id, "en", req.label_en)
            diff["label_en"] = req.label_en
        if req.label_km is not None:
            await self.repository.set_translation(symptom.id, "km", req.label_km)
            diff["label_km"] = req.label_km

        await self.session.flush()

        if diff:
            await self.audit.record(
                actor_id=user.id,
                action="update",
                entity_type="symptom",
                entity_id=symptom.id,
                diff=diff,
            )

        return await self.get_symptom(symptom.id, locale="en")

    async def delete_symptom(self, symptom_id: int, user: User) -> None:
        """Delete symptom ensuring no existing disease rules reference it."""
        symptom = await self.repository.get_by_id(symptom_id)
        if not symptom:
            raise NotFoundError(detail=f"Symptom with ID {symptom_id} not found")

        # Referential guard: check referencing disease_symptoms
        blocking = await self.repository.get_referencing_diseases(symptom_id)
        if blocking:
            names_str = ", ".join(blocking)
            msg = f"Cannot delete symptom: referenced by {len(blocking)} disease(s): {names_str}"
            raise ConflictError(detail=msg)

        await self.audit.record(
            actor_id=user.id,
            action="delete",
            entity_type="symptom",
            entity_id=symptom.id,
            diff={"code": symptom.code},
        )

        await self.repository.delete(symptom)
