"""AI module configuration.

Loads Ollama and AI-related settings from environment variables.
"""

from __future__ import annotations

import os
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not installed, rely on environment variables


class AIConfig:
    """Configuration for local AI integration."""

    # Ollama server configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # AI model selection (configurable)
    AI_MODEL: str = os.getenv("AI_MODEL", "qwen2.5:7b")
    AI_VISION_MODEL: str = os.getenv("AI_VISION_MODEL", "qwen2.5:7b")
    
    # Timeout settings (in seconds)
    AI_TIMEOUT: int = int(os.getenv("AI_TIMEOUT", "120"))
    AI_VISION_TIMEOUT: int = int(os.getenv("AI_VISION_TIMEOUT", "180"))
    
    # Temperature settings for generation
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_EXTRACTION_TEMPERATURE: float = float(os.getenv("AI_EXTRACTION_TEMPERATURE", "0.3"))
    
    # Image upload configuration
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    ALLOWED_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}
    DISEASE_IMAGES_DIR: str = os.getenv(
        "DISEASE_IMAGES_DIR",
        "uploads/disease_images"
    )
    
    # AI features toggle
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "true").lower() == "true"
    AI_VISION_ENABLED: bool = os.getenv("AI_VISION_ENABLED", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> tuple[bool, str]:
        """Validate AI configuration.
        
        Returns:
            (is_valid, error_message)
        """
        if not cls.AI_ENABLED:
            return False, "AI features are disabled"
        
        if not cls.OLLAMA_HOST:
            return False, "OLLAMA_HOST is not configured"
        
        if not cls.AI_MODEL:
            return False, "AI_MODEL is not configured"
        
        return True, ""


# Create a singleton instance
ai_config = AIConfig()
