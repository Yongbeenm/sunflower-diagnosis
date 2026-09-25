"""Vision service for image analysis using Qwen-VL or similar vision models."""

from __future__ import annotations

import base64
import logging
import re
from io import BytesIO
from typing import Any

from PIL import Image

from ai.config import ai_config
from ai.schemas.ai_schemas import ImageAnalysisResponse, ImageObservation
from ai.services.json_parser import extract_json_from_response
from ai.services.ollama_service import OllamaService, get_ollama_service
from ai.services.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class VisionService:
    """Service for plant disease image analysis."""
    
    def __init__(self, ollama_service: OllamaService | None = None) -> None:
        self.ollama = ollama_service or get_ollama_service()
    
    def validate_image(self, image_base64: str) -> tuple[bool, str]:
        """Validate image data.
        
        Args:
            image_base64: Base64-encoded image
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Remove data URL prefix if present
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]
            
            # Decode base64
            image_data = base64.b64decode(image_base64)
            
            # Check size
            size_mb = len(image_data) / (1024 * 1024)
            if size_mb > ai_config.MAX_IMAGE_SIZE_MB:
                return False, f"Image too large: {size_mb:.1f}MB (max {ai_config.MAX_IMAGE_SIZE_MB}MB)"
            
            # Try to open with PIL
            image = Image.open(BytesIO(image_data))
            image.verify()
            
            return True, ""
        
        except base64.binascii.Error:
            return False, "Invalid base64 encoding"
        except Exception as e:
            return False, f"Invalid image: {e}"
    
    def _prepare_image_data(self, image_base64: str) -> str:
        """Prepare image data for Ollama.
        
        Args:
            image_base64: Base64-encoded image
        
        Returns:
            Clean base64 string without data URL prefix
        """
        # Remove data URL prefix if present (e.g., "data:image/png;base64,")
        if "," in image_base64:
            return image_base64.split(",", 1)[1]
        return image_base64
    
    async def analyze_plant_image(
        self,
        image_base64: str,
        locale: str = "en",
        additional_context: str | None = None,
    ) -> ImageAnalysisResponse:
        """Analyze a plant disease image.
        
        Args:
            image_base64: Base64-encoded image
            locale: Language for response
            additional_context: Additional context from user
        
        Returns:
            ImageAnalysisResponse with structured observations
        
        Raises:
            ValueError: If image is invalid
            OllamaError: If analysis fails
        """
        # Validate image
        is_valid, error = self.validate_image(image_base64)
        if not is_valid:
            raise ValueError(error)
        
        # Prepare image data
        clean_image_data = self._prepare_image_data(image_base64)
        
        # Load image analysis prompt
        base_prompt = load_prompt("image_analysis")
        
        # Add locale-specific instructions
        if locale == "km":
            language_instruction = "\n\nProvide your analysis in Khmer language."
            base_prompt += language_instruction
        
        # Add additional context if provided
        if additional_context:
            base_prompt += f"\n\nAdditional context: {additional_context}"
        
        # Request structured output
        structured_request = """

Please present your analysis clearly:
1. Plant Part & Specimen: (identify the visible sunflower plant part, e.g. leaf, stalk, head, seedling)
2. Visual Observations: (color changes, lesion shape, margins, texture, spots, or mold)
3. Potential Sunflower Diseases: (select most consistent from the 20 sunflower diseases)
4. Recommended Next Steps: (guidance on confirming via the Sunflower Expert System)

Finally, at the very end, append a JSON code block with structured observations:
```json
{
  "crop_identified": "Sunflower (Helianthus annuus)",
  "crop_confidence": 0.95,
  "plant_parts": ["leaf"],
  "visible_symptoms": ["list of observed symptoms"],
  "color_abnormalities": ["yellowing", "browning"],
  "spots_lesions": ["description of lesions"],
  "pests_visible": [],
  "image_quality": "good",
  "possible_diseases": ["Sunflower Rust"]
}
```
"""
        full_prompt = base_prompt + structured_request
        
        try:
            # Get analysis from vision model
            response = await self.ollama.analyze_image(
                image_base64=clean_image_data,
                prompt=full_prompt,
            )
            
            # Extract structured data
            observation_data = self._extract_observations(response)
            
            # Default crop_identified to Sunflower if not identified
            if not observation_data.get("crop_identified") or observation_data.get("crop_identified") == "null":
                observation_data["crop_identified"] = "Sunflower (Helianthus annuus)"
                if not observation_data.get("crop_confidence"):
                    observation_data["crop_confidence"] = 0.90

            # Remove raw JSON code block from user-facing text
            clean_text = re.sub(r"```(?:json)?[\s\S]*?```", "", response).strip()
            # Also remove any dangling leading/trailing JSON braces if left unformatted
            clean_text = re.sub(r"^\s*\{[\s\S]*?\}\s*", "", clean_text).strip()
            clean_text = re.sub(r"\s*\{[\s\S]*?\}\s*$", "", clean_text).strip()
            
            # If the model only returned JSON or stripped text is too short, provide a formatted summary
            if not clean_text or len(clean_text) < 30:
                clean_text = self._build_readable_summary(observation_data)

            return ImageAnalysisResponse(
                observations=ImageObservation(**observation_data),
                analysis_text=clean_text,
                warning="This is visual analysis only. Diagnosis requires expert system evaluation.",
            )
        
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise
    
    def _build_readable_summary(self, obs: dict[str, Any]) -> str:
        """Build a clean, readable text summary from observation data."""
        lines = []
        crop = obs.get("crop_identified") or "Sunflower (Helianthus annuus)"
        lines.append(f"**Identified Crop:** {crop}")
        parts = obs.get("plant_parts", [])
        if parts:
            lines.append(f"**Plant Parts Visible:** {', '.join(parts)}")
        symps = obs.get("visible_symptoms", [])
        if symps:
            lines.append(f"**Visible Symptoms:** {', '.join(symps)}")
        spots = obs.get("spots_lesions", [])
        if spots:
            lines.append(f"**Spots / Lesions:** {', '.join(spots)}")
        diseases = obs.get("possible_diseases", [])
        if diseases:
            lines.append(f"\n**Potential Sunflower Disease Matches:**\n" + "\n".join(f"- {d}" for d in diseases))
        lines.append("\n**Recommendation:** Use the Sunflower Expert System diagnosis checklist to confirm these symptoms.")
        return "\n".join(lines)

    def _extract_observations(self, response: str) -> dict[str, Any]:
        """Extract structured observations from analysis response.
        
        Args:
            response: AI analysis text
        
        Returns:
            Observation data dict
        """
        # Try to extract JSON structure
        try:
            data = extract_json_from_response(response)
            return data
        except ValueError:
            # If no JSON found, return minimal structure
            logger.warning("Could not extract structured data from image analysis")
            return {
                "crop_identified": "Sunflower (Helianthus annuus)",
                "crop_confidence": 0.85,
                "plant_parts": [],
                "visible_symptoms": [],
                "color_abnormalities": [],
                "spots_lesions": [],
                "pests_visible": [],
                "image_quality": "unknown",
                "possible_diseases": [],
            }
    
    async def extract_symptoms_from_image(
        self,
        image_base64: str,
    ) -> dict[str, Any]:
        """Extract symptom information from image for diagnosis.
        
        This is a simplified extraction focused on symptoms that can feed
        into the expert system.
        
        Args:
            image_base64: Base64-encoded image
        
        Returns:
            Dict with extracted symptom information
        """
        analysis = await self.analyze_plant_image(image_base64)
        
        # Convert observations to symptom format
        return {
            "crop": analysis.observations.crop_identified,
            "plant_part": analysis.observations.plant_parts,
            "symptoms": analysis.observations.visible_symptoms,
            "color_changes": analysis.observations.color_abnormalities,
            "spots": analysis.observations.spots_lesions,
            "pests": analysis.observations.pests_visible,
            "possible_diseases": analysis.observations.possible_diseases,
            "confidence": analysis.observations.crop_confidence or 0.0,
        }


def get_vision_service() -> VisionService:
    """Get VisionService instance.
    
    Returns:
        VisionService instance
    """
    return VisionService()
