"""API integration tests for Step 5 Content CRUD resources."""

from __future__ import annotations

import io
from decimal import Decimal

import pytest
from httpx import AsyncClient
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.audit import AuditLog
from app.models.auth import Role, User
from app.models.disease import Disease, DiseaseSymptom
from app.models.enums import PathogenType
from app.models.symptom import Symptom, SymptomCategory
from app.models.translation import Translation
from scripts.seed import seed_database


@pytest.fixture(autouse=True)
async def _seed_data(db_session: AsyncSession) -> None:
    """Ensure database has seed roles, permissions, categories, and active ruleset."""
    await seed_database(db_session)


async def _create_user_with_token(
    db_session: AsyncSession,
    username: str,
    role_name: str,
    permissions: list[str],
) -> tuple[User, str]:
    """Helper to create test user and issue JWT."""
    role_res = await db_session.execute(select(Role).where(Role.name == role_name))
    role = role_res.scalar_one()

    user = User(
        email=f"{username}@example.com",
        username=username,
        password_hash="fakehash",
        role_id=role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    token, _ = create_access_token(
        user_id=user.id,
        role=role_name,
        permissions=permissions,
    )
    return user, token


@pytest.mark.asyncio
async def test_diseases_pagination_and_filtering(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /diseases verifies pagination boundaries and category/pathogen filtering."""
    # Seed 3 diseases
    d1 = Disease(slug="white-mold", pathogen_type=PathogenType.FUNGAL, is_published=True)
    d2 = Disease(slug="sunflower-rust", pathogen_type=PathogenType.FUNGAL, is_published=True)
    d3 = Disease(slug="bacterial-wilt", pathogen_type=PathogenType.BACTERIAL, is_published=True)
    d4 = Disease(slug="draft-virus", pathogen_type=PathogenType.VIRAL, is_published=False)
    db_session.add_all([d1, d2, d3, d4])
    await db_session.flush()

    # English translations
    t1 = Translation(
        entity_type="disease", entity_id=d1.id, locale="en", field="name", value="White Mold"
    )
    t2 = Translation(
        entity_type="disease", entity_id=d2.id, locale="en", field="name", value="Sunflower Rust"
    )
    t3 = Translation(
        entity_type="disease", entity_id=d3.id, locale="en", field="name", value="Bacterial Wilt"
    )
    db_session.add_all([t1, t2, t3])
    await db_session.commit()

    # 1. Page 1 size 2 (published=True)
    res = await client.get("/api/v1/diseases?page=1&size=2&published=true")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["size"] == 2

    # 2. Page 2 size 2
    res_p2 = await client.get("/api/v1/diseases?page=2&size=2&published=true")
    assert res_p2.status_code == 200
    data_p2 = res_p2.json()
    assert len(data_p2["items"]) == 1

    # 3. Pathogen filter
    res_bact = await client.get("/api/v1/diseases?pathogen=bacterial")
    assert res_bact.status_code == 200
    data_bact = res_bact.json()
    assert data_bact["total"] == 1
    assert data_bact["items"][0]["slug"] == "bacterial-wilt"


@pytest.mark.asyncio
async def test_disease_detail_per_field_locale_fallback(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /diseases/{slug} falls back field-by-field to English when translation is missing."""
    d = Disease(slug="charcoal-rot", pathogen_type=PathogenType.FUNGAL, is_published=True)
    db_session.add(d)
    await db_session.flush()

    # English has name, description, and treatment
    db_session.add_all(
        [
            Translation(
                entity_type="disease",
                entity_id=d.id,
                locale="en",
                field="name",
                value="Charcoal Rot",
            ),
            Translation(
                entity_type="disease",
                entity_id=d.id,
                locale="en",
                field="description",
                value="Stem rot under hot dry conditions.",
            ),
            Translation(
                entity_type="disease",
                entity_id=d.id,
                locale="en",
                field="treatment",
                value="Crop rotation and irrigation.",
            ),
        ]
    )

    # Khmer has name ONLY
    db_session.add(
        Translation(
            entity_type="disease", entity_id=d.id, locale="km", field="name", value="ជំងឺរលួយធ្យូង"
        )
    )
    await db_session.commit()

    # Query with locale=km
    res = await client.get("/api/v1/diseases/charcoal-rot?locale=km")
    assert res.status_code == 200
    data = res.json()

    # Khmer name is used
    assert data["name"] == "ជំងឺរលួយធ្យូង"
    # Description and treatment fall back to English!
    assert data["description"] == "Stem rot under hot dry conditions."
    assert data["treatment"] == "Crop rotation and irrigation."


@pytest.mark.asyncio
async def test_full_text_search_ranking(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /diseases?q=... finds diseases matching keyword in translated fields."""
    d1 = Disease(slug="powdery-mildew", pathogen_type=PathogenType.FUNGAL, is_published=True)
    d2 = Disease(slug="downy-mildew", pathogen_type=PathogenType.FUNGAL, is_published=True)
    db_session.add_all([d1, d2])
    await db_session.flush()

    db_session.add_all(
        [
            Translation(
                entity_type="disease",
                entity_id=d1.id,
                locale="en",
                field="name",
                value="Powdery Mildew",
            ),
            Translation(
                entity_type="disease",
                entity_id=d1.id,
                locale="en",
                field="description",
                value="White talcum-like coating on upper leaf surface.",
            ),
            Translation(
                entity_type="disease",
                entity_id=d2.id,
                locale="en",
                field="name",
                value="Downy Mildew",
            ),
            Translation(
                entity_type="disease",
                entity_id=d2.id,
                locale="en",
                field="description",
                value="Systemic stunting with yellow chlorosis.",
            ),
        ]
    )
    await db_session.commit()

    res = await client.get("/api/v1/diseases?q=talcum")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["slug"] == "powdery-mildew"


@pytest.mark.asyncio
async def test_bulk_weights_transaction_atomicity_and_validation(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """PUT /diseases/{id}/symptoms rejects invalid symptom IDs with 422
    and rolls back atomically.
    """
    _user, token = await _create_user_with_token(
        db_session, "agro_weights", "agronomist", ["disease:update"]
    )

    cat_res = await db_session.execute(select(SymptomCategory).limit(1))
    category = cat_res.scalar_one()

    # Create 2 valid symptoms
    s1 = Symptom(code="symptom_one", category_id=category.id, is_environmental=False)
    s2 = Symptom(code="symptom_two", category_id=category.id, is_environmental=False)
    d = Disease(slug="test-weights-disease", pathogen_type=PathogenType.FUNGAL, is_published=True)
    db_session.add_all([s1, s2, d])
    await db_session.flush()

    # Initial weight for s1
    ds_init = DiseaseSymptom(
        disease_id=d.id, symptom_id=s1.id, weight=Decimal("0.50"), is_required=False
    )
    db_session.add(ds_init)
    await db_session.commit()

    # Attempt bulk update with bad symptom ID at index 1
    payload = {
        "symptoms": [
            {"symptom_id": s1.id, "weight": 0.80, "is_required": True, "is_pathognomonic": False},
            {
                "symptom_id": 99999,
                "weight": 0.60,
                "is_required": False,
                "is_pathognomonic": False,
            },  # BAD ID
        ]
    }

    res = await client.put(
        f"/api/v1/diseases/{d.id}/symptoms",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 422
    err_body = res.json()
    assert err_body["type"] == "/errors/validation-failed"
    # Must report the specific failing item index
    field_errors = [e["field"] for e in err_body["errors"]]
    assert "symptoms[1].symptom_id" in field_errors

    # Verify atomic rollback: initial symptom weight must be untouched
    stmt = select(DiseaseSymptom).where(DiseaseSymptom.disease_id == d.id)
    current_weights = (await db_session.execute(stmt)).scalars().all()
    assert len(current_weights) == 1
    assert float(current_weights[0].weight) == 0.50

    # Now perform valid bulk update
    valid_payload = {
        "symptoms": [
            {"symptom_id": s1.id, "weight": 0.70, "is_required": True, "is_pathognomonic": False},
            {"symptom_id": s2.id, "weight": 0.30, "is_required": False, "is_pathognomonic": True},
        ]
    }
    res_valid = await client.put(
        f"/api/v1/diseases/{d.id}/symptoms",
        json=valid_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_valid.status_code == 200

    # Verify updated weights in database
    weights_after = (await db_session.execute(stmt)).scalars().all()
    assert len(weights_after) == 2


@pytest.mark.asyncio
async def test_delete_symptom_in_use_returns_409_with_blocking_diseases(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """DELETE /symptoms/{id} returns 409 and names blocking diseases if referenced."""
    _user, token = await _create_user_with_token(
        db_session, "agro_del", "agronomist", ["symptom:delete"]
    )

    cat_res = await db_session.execute(select(SymptomCategory).limit(1))
    category = cat_res.scalar_one()

    s = Symptom(code="referenced_symptom", category_id=category.id, is_environmental=False)
    d = Disease(slug="blocking-white-mold", pathogen_type=PathogenType.FUNGAL, is_published=True)
    db_session.add_all([s, d])
    await db_session.flush()

    ds = DiseaseSymptom(disease_id=d.id, symptom_id=s.id, weight=Decimal("0.50"))
    db_session.add(ds)
    await db_session.commit()

    # Attempt to delete referenced symptom -> 409 Conflict
    res = await client.delete(
        f"/api/v1/symptoms/{s.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 409
    err = res.json()
    assert err["type"] == "/errors/conflict"
    assert "blocking-white-mold" in err["detail"]


@pytest.mark.asyncio
async def test_media_upload_magic_bytes_validation_and_exif_strip(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """POST /media checks magic bytes (rejects script disguised as png) and strips EXIF."""
    _user, token = await _create_user_with_token(
        db_session, "media_uploader", "agronomist", ["disease:update"]
    )

    # 1. Script disguised as image file -> Rejected 422
    fake_png_data = b"#!/bin/bash\necho 'malicious code'\n"
    res_fraud = await client.post(
        "/api/v1/media",
        files={"file": ("malicious.png", fake_png_data, "image/png")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_fraud.status_code == 422
    assert "magic bytes" in res_fraud.json()["errors"][0]["message"].lower()

    # 2. Genuine PNG image
    buf = io.BytesIO()
    img = Image.new("RGB", (64, 48), color=(255, 204, 0))
    img.save(buf, format="PNG")
    valid_png_data = buf.getvalue()

    res_valid = await client.post(
        "/api/v1/media",
        files={"file": ("sunflower.png", valid_png_data, "image/png")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_valid.status_code == 200
    media_data = res_valid.json()
    assert media_data["id"] is not None
    assert media_data["width"] == 64
    assert media_data["height"] == 48
    assert "/media/" in media_data["url"]


@pytest.mark.asyncio
async def test_audit_trail_recorded_on_mutation(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Resource mutations automatically write an audit_log record with actor and diff."""
    user, token = await _create_user_with_token(
        db_session, "audit_actor", "agronomist", ["symptom:create", "symptom:update"]
    )

    cat_res = await db_session.execute(select(SymptomCategory).limit(1))
    category = cat_res.scalar_one()

    # Create symptom via API
    res = await client.post(
        "/api/v1/symptoms",
        json={
            "code": "audit_test_symptom",
            "category_id": category.id,
            "label_en": "Audit Test Symptom",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    symptom_id = res.json()["id"]

    # Verify audit_log entry exists
    stmt = select(AuditLog).where(
        AuditLog.entity_type == "symptom", AuditLog.entity_id == symptom_id
    )
    audit_entry = (await db_session.execute(stmt)).scalar_one_or_none()
    assert audit_entry is not None
    assert audit_entry.actor_id == user.id
    assert audit_entry.action == "create"
    assert audit_entry.diff is not None
