"""Symptom extraction service.

Converts natural language plant disease descriptions into structured
symptom data that can be mapped to the existing expert system.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.config import ai_config
from ai.schemas.ai_schemas import (
    ExtractedSymptom,
    SymptomExtractionRequest,
    SymptomExtractionResponse,
)
from ai.services.json_parser import extract_json_from_response
from ai.services.ollama_service import OllamaService, get_ollama_service
from ai.services.prompt_loader import load_prompt
from app.models.symptom import Symptom

logger = logging.getLogger(__name__)


class SymptomExtractor:
    """Service for extracting structured symptoms from natural language."""
    
    def __init__(self, ollama_service: OllamaService | None = None) -> None:
        self.ollama = ollama_service or get_ollama_service()
    
    async def extract_symptoms(
        self,
        message: str,
        locale: str = "en",
    ) -> ExtractedSymptom:
        """Extract structured symptom information from user message.
        
        Args:
            message: User's natural language description
            locale: Language of the message (en or km)
        
        Returns:
            ExtractedSymptom with structured data
        
        Raises:
            OllamaError: If extraction fails
        """
        # Load extraction prompt
        system_prompt = load_prompt("symptom_extraction")
        
        # Add locale-specific instruction
        if locale == "km":
            system_prompt += "\n\nNote: The user message is in Khmer. Extract symptoms and translate field values to English for database compatibility."
        
        # Create user message
        user_message = f"User message: {message}"
        
        try:
            # Request extraction with low temperature for consistency
            response = await self.ollama.generate(
                prompt=user_message,
                system=system_prompt,
                temperature=ai_config.AI_EXTRACTION_TEMPERATURE,
            )
            
            logger.info(f"AI response for symptom extraction: {response[:500]}")
            
            # Parse JSON response
            extracted_data = extract_json_from_response(response)
            logger.info(f"Extracted data: {extracted_data}")
            
            # Validate and create ExtractedSymptom
            result = ExtractedSymptom(**extracted_data)
            logger.info(f"Created ExtractedSymptom: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Symptom extraction failed: {e}", exc_info=True)
            logger.error(f"AI response was: {response if 'response' in locals() else 'N/A'}")
            # Return empty extraction with low confidence on failure
            return ExtractedSymptom(confidence=0.0)
    
    async def map_to_database_symptoms(
        self,
        extracted: ExtractedSymptom,
        db: AsyncSession,
    ) -> tuple[list[int], list[str]]:
        """Map extracted symptoms to database symptom IDs.
        
        This attempts to match the extracted natural language symptoms
        to actual symptom codes in the database.
        
        Args:
            extracted: Extracted symptom data
            db: Database session
        
        Returns:
            (matched_symptom_ids, unmapped_descriptions)
        """
        # Get all symptoms from database
        stmt = select(Symptom)
        result = await db.execute(stmt)
        all_symptoms = result.scalars().all()

        # Also get all translations for symptoms
        from app.models.translation import Translation
        import re

        trans_stmt = select(Translation).where(Translation.entity_type == "symptom")
        trans_res = await db.execute(trans_stmt)
        all_translations = trans_res.scalars().all()

        symptom_labels: dict[int, list[str]] = {}
        for trans in all_translations:
            symptom_labels.setdefault(trans.entity_id, []).append(trans.value.lower())
        
        # Build mapping of symptom codes and descriptions
        symptom_map: dict[str, int] = {}
        for symptom in all_symptoms:
            symptom_map[symptom.code.lower()] = symptom.id
        
        matched_ids: list[int] = []
        unmapped: list[str] = []
        
        # Try to match extracted symptoms to database
        all_extracted_terms = (
            extracted.symptoms +
            extracted.color_changes +
            extracted.spots +
            extracted.pests
        )

        # Stop words to ignore during token matching
        stop_words = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "of", "with", "is", "are", "some", "plant", "sunflower"}
        
        for term in all_extracted_terms:
            term_lower = term.lower()
            term_tokens = {w for w in re.findall(r"\w+", term_lower) if w not in stop_words and len(w) > 2}
            
            # Direct code match
            if term_lower in symptom_map:
                symptom_id = symptom_map[term_lower]
                if symptom_id not in matched_ids:
                    matched_ids.append(symptom_id)
                continue
            
            # Substring / partial code match
            matched = False
            for code, symptom_id in symptom_map.items():
                if code in term_lower or term_lower in code:
                    if symptom_id not in matched_ids:
                        matched_ids.append(symptom_id)
                        matched = True
                    break
            
            # Token overlap against code and translated labels
            if not matched and term_tokens:
                best_score = 0
                best_id = None
                for symptom in all_symptoms:
                    code_tokens = set(symptom.code.lower().split("_")) - stop_words
                    labels = symptom_labels.get(symptom.id, [])
                    label_tokens = set()
                    for lbl in labels:
                        label_tokens.update(re.findall(r"\w+", lbl.lower()))
                    label_tokens -= stop_words

                    overlap_code = len(term_tokens & code_tokens)
                    overlap_label = len(term_tokens & label_tokens)
                    score = overlap_code * 2 + overlap_label

                    if score > best_score and score >= 2:
                        best_score = score
                        best_id = symptom.id

                if best_id and best_id not in matched_ids:
                    matched_ids.append(best_id)
                    matched = True

            if not matched:
                unmapped.append(term)
        
        # Fallback: if no symptoms matched from extracted lists, scan extracted plant parts and terms
        if not matched_ids and all_extracted_terms:
            for symptom in all_symptoms:
                code_tokens = set(symptom.code.lower().split("_")) - stop_words
                labels = symptom_labels.get(symptom.id, [])
                label_tokens = set()
                for lbl in labels:
                    label_tokens.update(re.findall(r"\w+", lbl.lower()))
                
                for term in all_extracted_terms:
                    term_tokens = {w for w in re.findall(r"\w+", term.lower()) if w not in stop_words and len(w) > 2}
                    if term_tokens & code_tokens or term_tokens & label_tokens:
                        if symptom.id not in matched_ids:
                            matched_ids.append(symptom.id)
                            break
        
        return matched_ids, unmapped
    
    async def extract_and_map(
        self,
        request: SymptomExtractionRequest,
        db: AsyncSession,
    ) -> SymptomExtractionResponse:
        """Extract symptoms and map to database IDs in one call.
        
        Args:
            request: Extraction request
            db: Database session
        
        Returns:
            Complete extraction response with mapped IDs
        """
        # Extract symptoms from natural language
        extracted = await self.extract_symptoms(
            message=request.message,
            locale=request.locale,
        )
        
        # Map to database symptom IDs
        mapped_ids, unmapped = await self.map_to_database_symptoms(
            extracted=extracted,
            db=db,
        )
        
        return SymptomExtractionResponse(
            extracted=extracted,
            mapped_symptom_ids=mapped_ids,
            unmapped_descriptions=unmapped,
        )
    
    async def enhance_with_followup_questions(
        self,
        extracted: ExtractedSymptom,
        locale: str = "en",
    ) -> list[str]:
        """Generate follow-up questions to clarify symptoms.
        
        Based on what was extracted, generate relevant questions to get
        more complete symptom information.
        
        Args:
            extracted: Previously extracted symptom data
            locale: Language for questions
        
        Returns:
            List of follow-up questions
        """
        # Build context about what we know
        known_info = []
        if extracted.crop:
            known_info.append(f"Crop: {extracted.crop}")
        if extracted.plant_part:
            known_info.append(f"Affected parts: {', '.join(extracted.plant_part)}")
        if extracted.symptoms:
            known_info.append(f"Symptoms: {', '.join(extracted.symptoms)}")
        
        context = "\n".join(known_info) if known_info else "No symptoms described yet"
        
        # Build prompt for question generation
        question_prompt = f"""You are helping a farmer diagnose plant disease.

Current information:
{context}

Generate 2-3 specific follow-up questions to better understand the plant disease.
Focus on missing information like:
- Which plant parts are affected?
- What do the spots/lesions look like?
- How long has this been happening?
- Are environmental factors involved?
- How severe is the problem?

{"Generate questions in Khmer language." if locale == "km" else "Generate questions in English."}

Return ONLY a JSON array of question strings:
["question 1", "question 2", "question 3"]
"""
        
        try:
            response = await self.ollama.generate(
                prompt=question_prompt,
                temperature=0.7,
            )
            
            # Parse JSON array
            questions_data = extract_json_from_response(response)
            
            if isinstance(questions_data, list):
                return [str(q) for q in questions_data[:3]]
            elif isinstance(questions_data, dict) and "questions" in questions_data:
                return [str(q) for q in questions_data["questions"][:3]]
            else:
                return []
        
        except Exception as e:
            logger.warning(f"Failed to generate follow-up questions: {e}")
            return []


def get_symptom_extractor() -> SymptomExtractor:
    """Get SymptomExtractor instance.
    
    Returns:
        SymptomExtractor instance
    """
    return SymptomExtractor()
