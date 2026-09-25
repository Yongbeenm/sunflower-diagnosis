"""AI-assisted diagnosis and chat API routes.

These endpoints integrate local AI with the existing expert system.
The AI extracts symptoms from natural language, but the final diagnosis
comes from the existing rule-based expert system.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ai.config import ai_config
from ai.schemas.ai_schemas import (
    AIChatRequest,
    AIChatResponse,
    AIDiagnosisRequest,
    AIDiagnosisResponse,
    AIHealthResponse,
    DiseaseDraftRequest,
    DiseaseDraftResponse,
    DuplicateCheckRequest,
    DuplicateCheckResponse,
    ImageAnalysisRequest,
    ImageAnalysisResponse,
    ImageMatchDiseaseRequest,
    ImageMatchDiseaseResponse,
    MatchedDiseaseInfo,
    SymptomExtractionRequest,
    SymptomExtractionResponse,
)
from ai.services.admin_chat_service import get_admin_chat_service
from ai.services.chatbot_service import get_chatbot_service
from ai.services.disease_assistant import get_disease_assistant
from ai.services.ollama_service import OllamaError, get_ollama_service
from ai.services.symptom_extractor import get_symptom_extractor
from ai.services.vision_service import get_vision_service
from app.core.deps import get_current_user, get_db, require_permission
from app.models.auth import User
from app.models.disease import Disease, DiseaseSymptom
from app.models.symptom import Symptom
from app.models.translation import Translation
from app.repositories.diagnosis import DiagnosisRepository
from app.schemas.diagnosis import DiagnosisRequest
from app.services.engine.runner import DiagnosisRunner
from app.services.media.storage import LocalDiskBackend, S3MediaBackend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


# ============================================================================
# Health Check
# ============================================================================

@router.get(
    "/health",
    response_model=AIHealthResponse,
    summary="Check AI service health",
)
async def check_ai_health() -> AIHealthResponse:
    """Check if Ollama server is available and which models are loaded.
    
    Returns health status and available models.
    """
    if not ai_config.AI_ENABLED:
        return AIHealthResponse(
            ollama_available=False,
            status="disabled",
            error="AI features are disabled in configuration",
        )
    
    ollama = get_ollama_service()
    
    try:
        is_healthy, error, models = await ollama.check_health()
        
        if not is_healthy:
            return AIHealthResponse(
                ollama_available=False,
                status="error",
                error=error,
            )
        
        # Check if configured models are available
        model_loaded = None
        vision_model_loaded = None
        
        for model in models:
            if ai_config.AI_MODEL in model:
                model_loaded = model
            if ai_config.AI_VISION_MODEL in model:
                vision_model_loaded = model
        
        status_msg = "ready" if model_loaded else "model_not_loaded"
        
        return AIHealthResponse(
            ollama_available=True,
            model_loaded=model_loaded,
            vision_model_loaded=vision_model_loaded,
            status=status_msg,
            error=None if model_loaded else f"Model {ai_config.AI_MODEL} not found",
        )
    
    except Exception as e:
        return AIHealthResponse(
            ollama_available=False,
            status="error",
            error=str(e),
        )


# ============================================================================
# User Chat
# ============================================================================

@router.post(
    "/chat",
    response_model=AIChatResponse,
    summary="Chat with AI assistant",
)
async def chat_with_ai(
    request: AIChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AIChatResponse:
    """Conversational AI assistant for sunflower crop health and system operations."""
    if not ai_config.AI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are currently disabled",
        )
    
    user_role = current_user.role.name if current_user.role else "grower"
    chat_service = get_admin_chat_service()
    
    try:
        response = await chat_service.handle_admin_chat(
            request=request,
            db=db,
            user_role=user_role,
        )
        return response
    
    except OllamaError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e!s}",
        ) from e
    
    except Exception as e:
        logger.exception("Chat endpoint /ai/chat failed for user %s: %s", current_user.email, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {e!s}",
        ) from e


# ============================================================================
# Symptom Extraction
# ============================================================================

@router.post(
    "/extract-symptoms",
    response_model=SymptomExtractionResponse,
    summary="Extract symptoms from natural language",
)
async def extract_symptoms(
    request: SymptomExtractionRequest,
    current_user: Annotated[User, Depends(require_permission("diagnosis:run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SymptomExtractionResponse:
    """Extract structured symptom information from user's natural language description.
    
    Converts text like "My sunflower leaves have brown spots" into structured
    symptom data that can be mapped to database symptom IDs.
    """
    if not ai_config.AI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are currently disabled",
        )
    
    extractor = get_symptom_extractor()
    
    try:
        response = await extractor.extract_and_map(request, db)
        return response
    
    except OllamaError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e!s}",
        ) from e
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Symptom extraction failed: {e!s}",
        ) from e


# ============================================================================
# AI-Assisted Diagnosis
# ============================================================================

@router.post(
    "/diagnose",
    response_model=AIDiagnosisResponse,
    summary="AI-assisted diagnosis using expert system",
)
async def ai_assisted_diagnosis(
    request: AIDiagnosisRequest,
    current_user: Annotated[User, Depends(require_permission("diagnosis:run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AIDiagnosisResponse:
    """Diagnose plant disease using natural language description.
    
    Workflow:
    1. AI extracts symptoms from user's message
    2. Symptoms are mapped to database symptom IDs
    3. Existing expert system performs diagnosis
    4. AI generates natural language explanation
    
    The final diagnosis comes from the rule-based expert system, NOT the AI.
    """
    if not ai_config.AI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are currently disabled",
        )
    
    extractor = get_symptom_extractor()
    
    try:
        # Step 1: Extract symptoms from message (and image if provided)
        extracted = await extractor.extract_symptoms(
            message=request.message,
            locale=request.locale,
        )
        
        # If image provided, also extract from image and merge
        if request.image_base64:
            vision = get_vision_service()
            image_symptoms = await vision.extract_symptoms_from_image(
                image_base64=request.image_base64,
            )
            # Merge image symptoms with text symptoms
            # (simplified - in production, do smarter merging)
            extracted.symptoms.extend(image_symptoms.get("symptoms", []))
            extracted.plant_part.extend(image_symptoms.get("plant_part", []))
        
        # Step 2: Map to database symptom IDs
        mapped_ids, unmapped = await extractor.map_to_database_symptoms(
            extracted=extracted,
            db=db,
        )
        
        if not mapped_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not identify any known symptoms from your description. Please try describing more specific symptoms.",
            )
        
        # Step 3: Run existing expert system diagnosis
        # Build answers dict: symptom_id -> "yes"
        answers = {symptom_id: "yes" for symptom_id in mapped_ids}
        
        diagnosis_request = DiagnosisRequest(
            answers=answers,
            locale=request.locale,
        )
        
        repo = DiagnosisRepository(db)
        runner = DiagnosisRunner(repo)
        
        # Run diagnosis and persist session
        diagnosis_result = await runner.create_session(
            diagnosis_request,
            current_user,
        )
        
        # Step 4: Generate AI explanation
        explanation = await _generate_diagnosis_explanation(
            extracted=extracted,
            diagnosis_result=diagnosis_result.model_dump(),
            locale=request.locale,
        )
        
        return AIDiagnosisResponse(
            extracted_symptoms=extracted,
            diagnosis_session_id=str(diagnosis_result.session_id) if diagnosis_result.session_id else None,
            expert_system_results=diagnosis_result.model_dump(),
            ai_explanation=explanation,
        )
    
    except HTTPException:
        raise
    
    except OllamaError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e!s}",
        ) from e
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnosis failed: {e!s}",
        ) from e


async def _generate_diagnosis_explanation(
    extracted: any,
    diagnosis_result: dict,
    locale: str,
) -> str:
    """Generate natural language explanation of diagnosis results."""
    ollama = get_ollama_service()
    
    results = diagnosis_result.get("results", [])
    
    if not results:
        if locale == "km":
            return "យើងមិនអាចកំណត់ជំងឺដែលត្រូវគ្នាបានទេ។ សូមពិគ្រោះជាមួយអ្នកជំនាញកសិកម្ម។"
        return "We could not identify a matching disease. Please consult with an agronomist."
    
    top_disease = results[0]
    
    prompt = f"""Generate a clear, helpful explanation of these diagnosis results for a farmer.

Symptoms observed: {", ".join(extracted.symptoms)}
Plant parts affected: {", ".join(extracted.plant_part)}

Top diagnosis: {top_disease.get("disease", {}).get("name", "Unknown")}
Confidence: {top_disease.get("confidence", 0) * 100:.0f}%

{"Write in Khmer language." if locale == "km" else "Write in English."}

Be empathetic, clear, and actionable. Explain what the disease is, why it matches, and what to do next.
Keep it under 150 words.
"""
    
    try:
        explanation = await ollama.generate(prompt=prompt, temperature=0.7)
        return explanation
    except Exception:
        # Fallback
        if locale == "km":
            return f"ជំងឺដែលគ្រោងទុកគឺ {top_disease.get('disease', {}).get('name', 'Unknown')}។"
        return f"The suspected disease is {top_disease.get('disease', {}).get('name', 'Unknown')}."


# ============================================================================
# Image Analysis
# ============================================================================

@router.post(
    "/analyze-image",
    response_model=ImageAnalysisResponse,
    summary="Analyze plant disease image",
)
async def analyze_image(
    request: ImageAnalysisRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> ImageAnalysisResponse:
    """Analyze a plant image for disease symptoms using vision AI.
    
    Returns visible observations. This is NOT a diagnosis - use the
    diagnosis endpoint to get an expert system evaluation.
    """
    if not ai_config.AI_ENABLED or not ai_config.AI_VISION_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vision AI features are currently disabled",
        )
    
    vision = get_vision_service()
    
    try:
        response = await vision.analyze_plant_image(
            image_base64=request.image_base64,
            locale=request.locale,
            additional_context=request.additional_context,
        )
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    
    except OllamaError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e!s}",
        ) from e
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {e!s}",
        ) from e


# ============================================================================
# Image Match Disease (Upload Photo → Auto-Match Disease → Auto-Check Symptoms)
# ============================================================================

@router.post(
    "/image-match-disease",
    response_model=ImageMatchDiseaseResponse,
    summary="Analyze image and match to system disease with auto-checked symptoms",
)
async def image_match_disease(
    request: ImageMatchDiseaseRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ImageMatchDiseaseResponse:
    """Analyze an uploaded plant photo, match it against diseases in the database,
    and auto-select the matching symptoms for the user.

    Workflow:
    1. Vision AI analyzes the photo and identifies possible diseases
    2. Fuzzy-match AI output against disease names/slugs in the DB
    3. Look up the matched disease's symptom associations
    4. Return matched disease info + auto-checked symptom IDs
    5. Frontend navigates user to the disease page and auto-checks symptoms
    """
    if not ai_config.AI_ENABLED or not ai_config.AI_VISION_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vision AI features are currently disabled",
        )

    vision = get_vision_service()

    try:
        # Step 1: Analyze the image
        analysis = await vision.analyze_plant_image(
            image_base64=request.image_base64,
            locale=request.locale,
            additional_context=request.additional_context,
        )

        possible_diseases = list(analysis.observations.possible_diseases)

        # Step 2: Load all diseases from DB with translations
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = (
            select(Disease)
            .options(selectinload(Disease.disease_symptoms).selectinload(DiseaseSymptom.symptom))
            .options(selectinload(Disease.image_media))
            .where(Disease.is_published == True)  # noqa: E712
        )
        result = await db.execute(stmt)
        all_diseases = result.scalars().unique().all()

        # Load disease name translations
        disease_ids = [d.id for d in all_diseases]
        trans_stmt = select(Translation).where(
            Translation.entity_type == "disease",
            Translation.entity_id.in_(disease_ids),
            Translation.field == "name",
        )
        trans_result = await db.execute(trans_stmt)
        all_translations = trans_result.scalars().all()

        # Build lookup: disease_id -> {locale: name}
        name_map: dict[int, dict[str, str]] = {}
        for t in all_translations:
            name_map.setdefault(t.entity_id, {})[t.locale] = t.value

        # Fallback: if vision model didn't populate possible_diseases array, scan analysis_text
        if not possible_diseases and analysis.analysis_text:
            text_lower = analysis.analysis_text.lower()
            for disease in all_diseases:
                slug_name = disease.slug.replace("-", " ")
                if slug_name in text_lower:
                    possible_diseases.append(slug_name)
                d_names = name_map.get(disease.id, {})
                for loc_val in d_names.values():
                    if loc_val.lower() in text_lower:
                        possible_diseases.append(loc_val)

        if not possible_diseases:
            return ImageMatchDiseaseResponse(
                matched=False,
                observations=analysis.observations,
                analysis_text=analysis.analysis_text,
            )

        # Step 3: Fuzzy-match AI's possible diseases against DB
        import re as regex_mod

        best_match_disease = None
        best_match_score = 0.0
        best_match_name = ""

        for ai_disease_name in possible_diseases:
            ai_name_lower = ai_disease_name.lower().strip()
            # Normalize: remove common prefixes like "Sunflower "
            ai_name_clean = regex_mod.sub(r"^sunflower\s+", "", ai_name_lower)
            ai_tokens = set(regex_mod.findall(r"\w+", ai_name_clean))

            for disease in all_diseases:
                # Match against slug
                slug_clean = disease.slug.replace("-", " ")
                slug_tokens = set(slug_clean.split())

                # Match against translated names
                disease_names = name_map.get(disease.id, {})
                all_name_tokens: set[str] = set(slug_tokens)
                resolved_name = disease_names.get(request.locale) or disease_names.get("en", disease.slug.replace("-", " ").title())

                for locale_name in disease_names.values():
                    all_name_tokens.update(
                        regex_mod.findall(r"\w+", locale_name.lower())
                    )

                # Score: Jaccard-like overlap
                if not ai_tokens or not all_name_tokens:
                    continue
                overlap = len(ai_tokens & all_name_tokens)
                union = len(ai_tokens | all_name_tokens)
                score = overlap / union if union else 0.0

                # Boost score if slug directly appears in AI output or vice versa
                if slug_clean in ai_name_clean or ai_name_clean in slug_clean or slug_clean in ai_name_lower:
                    score = max(score, 0.88)

                # Exact substring match with any translated name
                for locale_name in disease_names.values():
                    loc_lower = locale_name.lower()
                    if ai_name_clean in loc_lower or loc_lower in ai_name_clean or loc_lower in ai_name_lower:
                        score = max(score, 0.92)

                if score > best_match_score:
                    best_match_score = score
                    best_match_disease = disease
                    best_match_name = resolved_name

        # Require a minimum match threshold
        MIN_MATCH_THRESHOLD = 0.30
        if not best_match_disease or best_match_score < MIN_MATCH_THRESHOLD:
            return ImageMatchDiseaseResponse(
                matched=False,
                observations=analysis.observations,
                analysis_text=analysis.analysis_text,
            )

        # Step 4: Get auto-checked symptom IDs from the matched disease and resolved names
        auto_symptom_ids: list[int] = []
        for ds in best_match_disease.disease_symptoms:
            auto_symptom_ids.append(ds.symptom_id)

        symptom_names: list[str] = []
        if auto_symptom_ids:
            sym_trans_stmt = select(Translation).where(
                Translation.entity_type == "symptom",
                Translation.entity_id.in_(auto_symptom_ids),
                Translation.field == "name",
            )
            sym_trans_res = await db.execute(sym_trans_stmt)
            sym_trans = sym_trans_res.scalars().all()
            sym_name_map: dict[int, dict[str, str]] = {}
            for st in sym_trans:
                sym_name_map.setdefault(st.entity_id, {})[st.locale] = st.value
            for sid in auto_symptom_ids:
                s_name = sym_name_map.get(sid, {}).get(request.locale) or sym_name_map.get(sid, {}).get("en")
                if s_name:
                    symptom_names.append(s_name)

        # Step 5: Build image URL if disease has an image
        image_url = None
        if best_match_disease.image_media:
            from app.core.config import get_settings
            settings = get_settings()
            image_url = f"{settings.MEDIA_PUBLIC_URL}/{best_match_disease.image_media.storage_key}"

        matched_disease = MatchedDiseaseInfo(
            disease_id=best_match_disease.id,
            slug=best_match_disease.slug,
            name=best_match_name,
            pathogen_type=best_match_disease.pathogen_type.value,
            confidence=round(best_match_score, 3),
            image_url=image_url,
        )

        return ImageMatchDiseaseResponse(
            matched=True,
            disease=matched_disease,
            auto_checked_symptom_ids=auto_symptom_ids,
            symptom_names=symptom_names,
            observations=analysis.observations,
            analysis_text=analysis.analysis_text,
            navigate_to=f"/diseases/{best_match_disease.slug}",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except OllamaError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e!s}",
        ) from e

    except Exception as e:
        logger.exception("Image match disease failed for user %s: %s", current_user.email, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image disease matching failed: {e!s}",
        ) from e


# ============================================================================
# Admin/Expert Chat with Database Modification
# ============================================================================

@router.post(
    "/admin/chat",
    response_model=AIChatResponse,
    summary="Admin AI chat with database modification capabilities",
)
async def admin_chat(
    request: AIChatRequest,
    current_user: Annotated[User, Depends(require_permission("disease:read"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AIChatResponse:
    """AI assistant for admins and experts with database modification capabilities.
    
    This endpoint allows admin/expert users to:
    - List all diseases and symptoms
    - Create new diseases (requires disease:create permission)
    - Update existing diseases (requires disease:update permission)
    - Delete diseases (requires disease:delete permission)
    - Search for diseases and symptoms
    
    The AI understands natural language commands like:
    - "List all diseases"
    - "Create disease Powdery Mildew with pathogen fungal"
    - "Update disease Rust description to affects leaves"
    - "Delete disease Test Disease"
    - "Search for downy"
    
    **Permissions Required:**
    - View operations: disease:read
    - Create operations: disease:create
    - Update operations: disease:update
    - Delete operations: disease:delete (admin only)
    """
    if not ai_config.AI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are currently disabled",
        )
    
    # Get user's highest role
    user_role = current_user.role.name if current_user.role else "grower"
    
    admin_chat_service = get_admin_chat_service()
    
    try:
        response = await admin_chat_service.handle_admin_chat(
            request=request,
            db=db,
            user_role=user_role,
        )
        return response
    
    except OllamaError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e!s}",
        ) from e
    
    except Exception as e:
        logger.exception("Admin chat endpoint failed for user %s: %s", current_user.email, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Admin chat failed: {e!s}",
        ) from e


# ============================================================================
# Admin/Expert Endpoints
# ============================================================================

@router.post(
    "/expert/disease-draft",
    response_model=DiseaseDraftResponse,
    summary="Generate disease knowledge draft",
)
async def generate_disease_draft(
    request: DiseaseDraftRequest,
    current_user: Annotated[User, Depends(require_permission("disease:create"))],
) -> DiseaseDraftResponse:
    """Generate AI-assisted disease knowledge base draft for expert review.
    
    IMPORTANT: This is a DRAFT only. Experts must review, edit, and
    explicitly approve before it becomes official knowledge.
    """
    if not ai_config.AI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are currently disabled",
        )
    
    assistant = get_disease_assistant()
    
    try:
        response = await assistant.generate_disease_draft(request)
        return response
    
    except OllamaError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e!s}",
        ) from e
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Draft generation failed: {e!s}",
        ) from e


@router.post(
    "/expert/duplicate-check",
    response_model=DuplicateCheckResponse,
    summary="Check for duplicate diseases",
)
async def check_duplicate_disease(
    request: DuplicateCheckRequest,
    current_user: Annotated[User, Depends(require_permission("disease:create"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DuplicateCheckResponse:
    """Check if a proposed disease might be a duplicate of existing entries.
    
    Compares disease name, symptoms, and characteristics with existing
    diseases to identify potential duplicates.
    """
    if not ai_config.AI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are currently disabled",
        )
    
    assistant = get_disease_assistant()
    
    try:
        response = await assistant.check_duplicate_disease(request, db)
        return response
    
    except OllamaError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e!s}",
        ) from e
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Duplicate check failed: {e!s}",
        ) from e
