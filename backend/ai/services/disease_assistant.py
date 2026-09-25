"""Disease assistant service for admin/expert knowledge base management.

Helps experts create, edit, and validate disease knowledge entries.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.schemas.ai_schemas import (
    DiseaseDraft,
    DiseaseDraftRequest,
    DiseaseDraftResponse,
    DuplicateCheckRequest,
    DuplicateCheckResponse,
    DuplicateMatch,
)
from ai.services.json_parser import extract_json_from_response
from ai.services.ollama_service import OllamaService, get_ollama_service
from ai.services.prompt_loader import load_prompt
from ai.services.vision_service import VisionService
from app.models.disease import Disease

logger = logging.getLogger(__name__)


class DiseaseAssistant:
    """AI assistant for disease knowledge base management."""
    
    def __init__(
        self,
        ollama_service: OllamaService | None = None,
        vision_service: VisionService | None = None,
    ) -> None:
        self.ollama = ollama_service or get_ollama_service()
        self.vision = vision_service or VisionService(ollama_service=self.ollama)
    
    async def generate_disease_draft(
        self,
        request: DiseaseDraftRequest,
    ) -> DiseaseDraftResponse:
        """Generate a disease knowledge base draft from expert description.
        
        Args:
            request: Draft generation request
        
        Returns:
            Draft response with AI-generated content
        """
        # Load disease expert prompt
        system_prompt = load_prompt("disease_expert")
        
        # Add locale instruction
        if request.locale == "km":
            system_prompt += "\n\nThe expert's description is in Khmer. Generate English content and translate to Khmer where appropriate."
        
        # Build the generation prompt
        user_prompt = f"Expert description:\n{request.description}"
        
        # If image is provided, analyze it first
        image_context = ""
        if request.image_base64:
            try:
                image_analysis = await self.vision.analyze_plant_image(
                    image_base64=request.image_base64,
                    locale=request.locale,
                )
                image_context = f"\n\nImage analysis:\n{image_analysis.analysis_text}"
                user_prompt += image_context
            except Exception as e:
                logger.warning(f"Image analysis failed during draft generation: {e}")
        
        user_prompt += "\n\nGenerate a comprehensive disease knowledge entry as JSON."
        
        try:
            # Generate draft with moderate temperature for creativity
            response = await self.ollama.generate(
                prompt=user_prompt,
                system=system_prompt,
                temperature=0.5,
            )
            
            # Parse JSON response
            draft_data = extract_json_from_response(response)
            
            # Create and validate draft
            draft = DiseaseDraft(**draft_data)
            
            return DiseaseDraftResponse(
                draft=draft,
                status="draft",
                warning="This is AI-generated content. Expert review and approval required.",
            )
        
        except Exception as e:
            logger.error(f"Disease draft generation failed: {e}")
            raise
    
    async def check_duplicate_disease(
        self,
        request: DuplicateCheckRequest,
        db: AsyncSession,
    ) -> DuplicateCheckResponse:
        """Check if a disease might be a duplicate of existing entries.
        
        Args:
            request: Duplicate check request
            db: Database session
        
        Returns:
            Duplicate check response with matches
        """
        # Get all existing diseases with translations
        stmt = select(Disease).where(Disease.is_published == True)  # noqa: E712
        result = await db.execute(stmt)
        existing_diseases = result.scalars().all()
        
        if not existing_diseases:
            return DuplicateCheckResponse(
                is_likely_duplicate=False,
                matches=[],
                recommendation="No existing diseases to compare against.",
            )
        
        # Build context about existing diseases
        diseases_context = []
        for disease in existing_diseases[:50]:  # Limit to avoid context overflow
            disease_info = {
                "id": disease.id,
                "slug": disease.slug,
                "pathogen_type": disease.pathogen_type.value if disease.pathogen_type else None,
            }
            diseases_context.append(disease_info)
        
        # Load duplicate check prompt
        system_prompt = load_prompt("duplicate_check")
        
        # Build comparison prompt
        user_prompt = f"""Proposed disease:
Name: {request.disease_name}
Description: {request.description or "Not provided"}
Symptoms: {", ".join(request.symptoms) if request.symptoms else "Not provided"}

Existing diseases in database:
{diseases_context}

Analyze for potential duplicates and return JSON with similarity assessment.
"""
        
        try:
            response = await self.ollama.generate(
                prompt=user_prompt,
                system=system_prompt,
                temperature=0.3,  # Low temperature for consistency
            )
            
            # Parse response
            result_data = extract_json_from_response(response)
            
            # Build matches list
            matches = []
            for match_data in result_data.get("matches", []):
                matches.append(DuplicateMatch(**match_data))
            
            is_duplicate = result_data.get("is_likely_duplicate", False)
            recommendation = result_data.get(
                "recommendation",
                "Review suggested matches carefully.",
            )
            
            return DuplicateCheckResponse(
                is_likely_duplicate=is_duplicate,
                matches=matches,
                recommendation=recommendation,
            )
        
        except Exception as e:
            logger.error(f"Duplicate check failed: {e}")
            # Return safe default on failure
            return DuplicateCheckResponse(
                is_likely_duplicate=False,
                matches=[],
                recommendation=f"Duplicate check failed: {e}. Manual review recommended.",
            )
    
    async def suggest_symptom_weights(
        self,
        disease_name: str,
        disease_description: str,
        symptoms: list[str],
    ) -> dict[str, float]:
        """Suggest symptom weights for a disease.
        
        Based on disease description and symptoms, suggest appropriate
        weights for the expert system rules.
        
        Args:
            disease_name: Name of disease
            disease_description: Description
            symptoms: List of symptom descriptions
        
        Returns:
            Dict mapping symptom to suggested weight (0.0 to 1.0)
        """
        prompt = f"""You are helping an expert assign weights to symptoms for a plant disease expert system.

Disease: {disease_name}
Description: {disease_description}

Symptoms to weight: {", ".join(symptoms)}

For each symptom, assign a weight between 0.0 and 1.0 where:
- 1.0 = pathognomonic (uniquely identifying symptom)
- 0.7-0.9 = highly characteristic
- 0.4-0.6 = common symptom
- 0.1-0.3 = possible but not specific

Return ONLY a JSON object mapping symptom to weight:
{{
  "symptom1": 0.8,
  "symptom2": 0.6,
  ...
}}
"""
        
        try:
            response = await self.ollama.generate(
                prompt=prompt,
                temperature=0.3,
            )
            
            weights = extract_json_from_response(response)
            
            # Validate weights are in range
            validated_weights = {}
            for symptom, weight in weights.items():
                weight_float = float(weight)
                if 0.0 <= weight_float <= 1.0:
                    validated_weights[symptom] = weight_float
                else:
                    validated_weights[symptom] = 0.5  # Default moderate weight
            
            return validated_weights
        
        except Exception as e:
            logger.warning(f"Weight suggestion failed: {e}")
            # Return default moderate weights
            return {symptom: 0.5 for symptom in symptoms}
    
    async def translate_disease_content(
        self,
        content: dict[str, str],
        source_locale: str,
        target_locale: str,
    ) -> dict[str, str]:
        """Translate disease content between languages.
        
        Args:
            content: Dict of field names to content
            source_locale: Source language (en or km)
            target_locale: Target language (en or km)
        
        Returns:
            Translated content dict
        """
        if source_locale == target_locale:
            return content
        
        language_names = {
            "en": "English",
            "km": "Khmer",
        }
        
        source_lang = language_names.get(source_locale, "Unknown")
        target_lang = language_names.get(target_locale, "Unknown")
        
        # Build translation prompt
        content_text = "\n\n".join([f"{k}: {v}" for k, v in content.items()])
        
        prompt = f"""Translate the following plant disease content from {source_lang} to {target_lang}.
Maintain technical accuracy and use appropriate agricultural terminology.

{content_text}

Return ONLY a JSON object with the same field names but translated values.
"""
        
        try:
            response = await self.ollama.generate(
                prompt=prompt,
                temperature=0.3,
            )
            
            translated = extract_json_from_response(response)
            return translated
        
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Return original on failure
            return content


def get_disease_assistant() -> DiseaseAssistant:
    """Get DiseaseAssistant instance.
    
    Returns:
        DiseaseAssistant instance
    """
    return DiseaseAssistant()
