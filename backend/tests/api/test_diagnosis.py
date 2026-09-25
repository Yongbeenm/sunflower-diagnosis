"""API integration tests for diagnosis evaluation, preview, persistence, and authorization."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.auth import Role, User
from app.models.diagnosis import DiagnosisResult, DiagnosisSelectedSymptom, DiagnosisSession
from app.models.disease import Disease, DiseaseSymptom
from app.models.enums import DiagnosisOutcome
from app.models.symptom import Symptom, SymptomCategory
from app.models.translation import Translation
from scripts.seed import seed_database


@pytest.fixture(autouse=True)
async def _setup_seed_and_rules(db_session: AsyncSession) -> None:
    """Seed base database and provide sample diseases and symptoms for testing."""
    await seed_database(db_session)

    # Fetch existing category from seed
    cat_res = await db_session.execute(select(SymptomCategory).limit(1))
    category = cat_res.scalar_one()

    # Create test symptoms
    s1 = Symptom(code="white_fuzzy_mold", category_id=category.id, is_environmental=False)
    s2 = Symptom(code="soft_head_rot", category_id=category.id, is_environmental=False)
    s3 = Symptom(code="orange_pustules", category_id=category.id, is_environmental=False)
    s4 = Symptom(code="cool_wet_weather", category_id=category.id, is_environmental=True)
    db_session.add_all([s1, s2, s3, s4])
    await db_session.flush()

    # Create test diseases (published)
    d1 = Disease(slug="white-mold", pathogen_type="fungal", is_published=True)
    d2 = Disease(slug="sunflower-rust", pathogen_type="fungal", is_published=True)
    # Unpublished disease to verify it is omitted from engine
    d_draft = Disease(slug="draft-disease", pathogen_type="fungal", is_published=False)
    db_session.add_all([d1, d2, d_draft])
    await db_session.flush()

    # Translations for disease names
    t1 = Translation(
        entity_type="disease", entity_id=d1.id, locale="en", field="name", value="White Mold"
    )
    t2 = Translation(
        entity_type="disease", entity_id=d2.id, locale="en", field="name", value="Sunflower Rust"
    )
    db_session.add_all([t1, t2])

    # Disease symptoms
    ds1 = DiseaseSymptom(
        disease_id=d1.id, symptom_id=s1.id, weight=Decimal("0.60"), is_pathognomonic=True
    )
    ds2 = DiseaseSymptom(
        disease_id=d1.id, symptom_id=s2.id, weight=Decimal("0.40"), is_required=False
    )
    ds3 = DiseaseSymptom(
        disease_id=d1.id, symptom_id=s4.id, weight=Decimal("0.30"), is_required=False
    )

    ds4 = DiseaseSymptom(
        disease_id=d2.id, symptom_id=s3.id, weight=Decimal("0.70"), is_required=False
    )
    ds5 = DiseaseSymptom(
        disease_id=d2.id, symptom_id=s4.id, weight=Decimal("0.30"), is_required=False
    )

    db_session.add_all([ds1, ds2, ds3, ds4, ds5])
    await db_session.commit()


async def _create_test_user(
    db_session: AsyncSession,
    username: str,
    role_name: str,
) -> tuple[User, str]:
    """Helper to create user and issue access token."""
    role_res = await db_session.execute(select(Role).where(Role.name == role_name))
    role = role_res.scalar_one()

    user = User(
        email=f"{username}@example.com",
        username=username,
        password_hash="testhash",
        role_id=role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    token_permissions = (
        ["diagnosis:run", "diagnosis:read_own", "diagnosis:read_all"]
        if role_name == "agronomist"
        else ["diagnosis:run", "diagnosis:read_own"]
    )
    token, _ = create_access_token(
        user_id=user.id,
        role=role_name,
        permissions=token_permissions,
    )
    return user, token


@pytest.mark.asyncio
async def test_preview_writes_nothing_to_database(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """POST /diagnosis/preview evaluates rules without persisting sessions or results."""
    _user, token = await _create_test_user(db_session, "preview_user", "grower")

    # Fetch symptom id
    s_res = await db_session.execute(select(Symptom).where(Symptom.code == "white_fuzzy_mold"))
    symptom = s_res.scalar_one()

    # Pre-count database rows
    pre_sessions = (await db_session.execute(select(DiagnosisSession))).scalars().all()
    pre_results = (await db_session.execute(select(DiagnosisResult))).scalars().all()

    payload = {
        "locale": "en",
        "answers": {str(symptom.id): "yes"},
    }
    response = await client.post(
        "/api/v1/diagnosis/preview",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] is None
    assert data["outcome"] == "matched"
    assert len(data["results"]) >= 1
    assert data["results"][0]["disease"]["slug"] == "white-mold"
    assert data["results"][0]["disease"]["name"] == "White Mold"
    assert "evidence" in data["results"][0]
    assert len(data["results"][0]["evidence"]["supporting"]) >= 1

    # Verify zero database writes occurred
    post_sessions = (await db_session.execute(select(DiagnosisSession))).scalars().all()
    post_results = (await db_session.execute(select(DiagnosisResult))).scalars().all()
    assert len(post_sessions) == len(pre_sessions)
    assert len(post_results) == len(pre_results)


@pytest.mark.asyncio
async def test_diagnosis_sessions_persistence_roundtrip(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """POST /diagnosis/sessions persists session, answers, and results with JSONB evidence."""
    user, token = await _create_test_user(db_session, "roundtrip_user", "grower")

    s_res = await db_session.execute(select(Symptom).where(Symptom.code == "white_fuzzy_mold"))
    s1 = s_res.scalar_one()
    s2_res = await db_session.execute(select(Symptom).where(Symptom.code == "orange_pustules"))
    s2 = s2_res.scalar_one()

    payload = {
        "locale": "en",
        "answers": {
            str(s1.id): "yes",
            str(s2.id): "no",
        },
    }

    response = await client.post(
        "/api/v1/diagnosis/sessions",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] is not None
    session_id_str = data["session_id"]
    assert data["outcome"] == "matched"
    assert data["results"][0]["disease"]["slug"] == "white-mold"

    # Verify database persistence
    session_uuid = uuid.UUID(session_id_str)
    stmt = select(DiagnosisSession).where(DiagnosisSession.id == session_uuid)
    saved_session = (await db_session.execute(stmt)).scalar_one_or_none()
    assert saved_session is not None
    assert saved_session.user_id == user.id
    assert saved_session.symptom_count == 2
    assert saved_session.outcome == DiagnosisOutcome.MATCHED

    # Verify selected symptoms stored
    sel_stmt = select(DiagnosisSelectedSymptom).where(
        DiagnosisSelectedSymptom.session_id == session_uuid
    )
    selected = (await db_session.execute(sel_stmt)).scalars().all()
    assert len(selected) == 2

    # Verify results and JSONB evidence stored
    res_stmt = select(DiagnosisResult).where(DiagnosisResult.session_id == session_uuid)
    results = (await db_session.execute(res_stmt)).scalars().all()
    assert len(results) >= 1
    top_result = results[0]
    assert top_result.disease_name_snapshot == "White Mold"
    assert "supporting" in top_result.evidence

    # GET /diagnosis/sessions/{id} retrieves the round-trip detail
    get_res = await client.get(
        f"/api/v1/diagnosis/sessions/{session_id_str}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["session_id"] == session_id_str
    assert detail["outcome"] == "matched"
    assert len(detail["selected_symptoms"]) == 2
    assert len(detail["results"]) >= 1


@pytest.mark.asyncio
async def test_no_match_path_persists_empty_results_with_feedback_prompt(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Empty ranking persists outcome='no_match' with top_disease NULL and feedback_prompt."""
    _user, token = await _create_test_user(db_session, "nomatch_user", "grower")

    s_res = await db_session.execute(select(Symptom).where(Symptom.code == "orange_pustules"))
    symptom = s_res.scalar_one()

    # Answering "no" to the only symptom should produce an empty ranking
    payload = {
        "locale": "en",
        "answers": {str(symptom.id): "no"},
    }

    response = await client.post(
        "/api/v1/diagnosis/sessions",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] is not None
    assert data["outcome"] == "no_match"
    assert data["results"] == []
    assert data["feedback_prompt"] is not None
    assert "feedback" in data["feedback_prompt"].lower()

    # Check database record
    session_uuid = uuid.UUID(data["session_id"])
    saved = (
        await db_session.execute(
            select(DiagnosisSession).where(DiagnosisSession.id == session_uuid)
        )
    ).scalar_one()
    assert saved.outcome == DiagnosisOutcome.NO_MATCH
    assert saved.top_disease_id is None
    assert saved.top_confidence is None


@pytest.mark.asyncio
async def test_session_privacy_user_a_gets_404_for_user_b(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """User A gets 404 (not 403) for User B's session to prevent existence leakage."""
    _user_a, token_a = await _create_test_user(db_session, "user_a", "grower")
    _user_b, token_b = await _create_test_user(db_session, "user_b", "grower")

    s_res = await db_session.execute(select(Symptom).where(Symptom.code == "white_fuzzy_mold"))
    s = s_res.scalar_one()

    # User B creates a session
    post_res = await client.post(
        "/api/v1/diagnosis/sessions",
        json={"locale": "en", "answers": {str(s.id): "yes"}},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert post_res.status_code == 200
    session_id = post_res.json()["session_id"]

    # User A tries to view User B's session -> must receive 404, not 403
    get_res = await client.get(
        f"/api/v1/diagnosis/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert get_res.status_code == 404
    err = get_res.json()
    assert err["type"] == "/errors/not-found"
    assert "not found" in err["detail"].lower()


@pytest.mark.asyncio
async def test_diagnosis_read_all_allows_agronomist_to_view_other_sessions(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """User with diagnosis:read_all (e.g. agronomist) can view another grower's session."""
    _grower, grower_token = await _create_test_user(db_session, "field_grower", "grower")
    _agronomist, agro_token = await _create_test_user(db_session, "field_agronomist", "agronomist")

    s_res = await db_session.execute(select(Symptom).where(Symptom.code == "white_fuzzy_mold"))
    s = s_res.scalar_one()

    # Grower creates a session
    post_res = await client.post(
        "/api/v1/diagnosis/sessions",
        json={"locale": "en", "answers": {str(s.id): "yes"}},
        headers={"Authorization": f"Bearer {grower_token}"},
    )
    assert post_res.status_code == 200
    session_id = post_res.json()["session_id"]

    # Agronomist accesses grower's session -> 200 OK
    get_res = await client.get(
        f"/api/v1/diagnosis/sessions/{session_id}",
        headers={"Authorization": f"Bearer {agro_token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["session_id"] == session_id


@pytest.mark.asyncio
async def test_paginated_user_history(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /diagnosis/sessions returns paginated list of own sessions only."""
    _user, token = await _create_test_user(db_session, "history_grower", "grower")
    _other, other_token = await _create_test_user(db_session, "other_grower", "grower")

    s_res = await db_session.execute(select(Symptom).where(Symptom.code == "white_fuzzy_mold"))
    s = s_res.scalar_one()

    # Create 3 sessions for user
    for _ in range(3):
        await client.post(
            "/api/v1/diagnosis/sessions",
            json={"locale": "en", "answers": {str(s.id): "yes"}},
            headers={"Authorization": f"Bearer {token}"},
        )

    # Create 1 session for other user
    await client.post(
        "/api/v1/diagnosis/sessions",
        json={"locale": "en", "answers": {str(s.id): "yes"}},
        headers={"Authorization": f"Bearer {other_token}"},
    )

    # Fetch page 1 with size 2
    res_p1 = await client.get(
        "/api/v1/diagnosis/sessions?page=1&size=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_p1.status_code == 200
    data_p1 = res_p1.json()
    assert data_p1["total"] == 3
    assert len(data_p1["items"]) == 2
    assert data_p1["page"] == 1
    assert data_p1["size"] == 2

    # Fetch page 2 with size 2
    res_p2 = await client.get(
        "/api/v1/diagnosis/sessions?page=2&size=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_p2.status_code == 200
    data_p2 = res_p2.json()
    assert len(data_p2["items"]) == 1
    assert data_p2["page"] == 2
