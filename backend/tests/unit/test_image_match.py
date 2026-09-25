"""Unit tests for Image Match Disease schema and response validation."""

import pytest
from ai.schemas.ai_schemas import (
    ImageMatchDiseaseRequest,
    ImageMatchDiseaseResponse,
    MatchedDiseaseInfo,
    ImageObservation,
)


def test_image_match_disease_request():
    """Test valid image match request creation."""
    req = ImageMatchDiseaseRequest(
        image_base64="aGVsbG8=",
        locale="en",
        additional_context="Yellow spots on lower leaves",
    )
    assert req.image_base64 == "aGVsbG8="
    assert req.locale == "en"
    assert req.additional_context == "Yellow spots on lower leaves"


def test_image_match_disease_response_unmatched():
    """Test response when photo does not match any DB disease."""
    resp = ImageMatchDiseaseResponse(
        matched=False,
        observations=ImageObservation(visible_symptoms=["yellow spots"]),
        analysis_text="Symptoms observed but no definitive system disease matched.",
    )
    assert not resp.matched
    assert resp.disease is None
    assert resp.auto_checked_symptom_ids == []
    assert resp.navigate_to is None


def test_image_match_disease_response_matched():
    """Test response when photo matches sunflower rust in the system DB."""
    matched = MatchedDiseaseInfo(
        disease_id=3,
        slug="sunflower-rust",
        name="Sunflower Rust (Puccinia helianthi)",
        pathogen_type="fungal",
        confidence=0.92,
        image_url="/media/rust.jpg",
    )
    resp = ImageMatchDiseaseResponse(
        matched=True,
        disease=matched,
        auto_checked_symptom_ids=[10, 11, 12],
        symptom_names=[
            "Cinnamon-brown powdery pustules",
            "Premature leaf drying",
            "Black telia pustules late season",
        ],
        observations=ImageObservation(
            possible_diseases=["Sunflower Rust"],
            visible_symptoms=["cinnamon pustules"],
        ),
        analysis_text="The sunflower leaf shows distinct cinnamon-brown pustules typical of Sunflower Rust.",
        navigate_to="/diseases/sunflower-rust",
    )
    assert resp.matched
    assert resp.disease.slug == "sunflower-rust"
    assert resp.disease.confidence == 0.92
    assert resp.auto_checked_symptom_ids == [10, 11, 12]
    assert len(resp.symptom_names) == 3
    assert resp.navigate_to == "/diseases/sunflower-rust"
