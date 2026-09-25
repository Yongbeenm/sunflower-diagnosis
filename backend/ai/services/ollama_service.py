"""Ollama service for local AI model communication.

This service handles all communication with the local Ollama server.
It supports both text-only chat and vision (multimodal) interactions.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ai.config import ai_config

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Base exception for Ollama-related errors."""
    pass


class OllamaConnectionError(OllamaError):
    """Raised when unable to connect to Ollama server."""
    pass


class OllamaTimeoutError(OllamaError):
    """Raised when Ollama request times out."""
    pass


class OllamaService:
    """Service for interacting with local Ollama server."""
    
    def __init__(self) -> None:
        self.base_url = ai_config.OLLAMA_HOST
        self.model = ai_config.AI_MODEL
        self.vision_model = ai_config.AI_VISION_MODEL
        self.timeout = ai_config.AI_TIMEOUT
        self.vision_timeout = ai_config.AI_VISION_TIMEOUT
    
    async def _make_request(
        self,
        endpoint: str,
        payload: dict[str, Any],
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to Ollama server.
        
        Args:
            endpoint: API endpoint (e.g., '/api/generate', '/api/chat')
            payload: Request payload
            timeout: Request timeout in seconds (uses default if None)
        
        Returns:
            Response JSON
        
        Raises:
            OllamaConnectionError: Cannot connect to Ollama
            OllamaTimeoutError: Request timed out
            OllamaError: Other Ollama errors
        """
        url = f"{self.base_url}{endpoint}"
        timeout_val = timeout if timeout is not None else self.timeout
        
        try:
            async with httpx.AsyncClient(timeout=timeout_val) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}: {e}")
            raise OllamaConnectionError(
                f"Cannot connect to Ollama server at {self.base_url}. "
                f"Is Ollama running?"
            ) from e
        
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timed out after {timeout_val}s: {e}")
            raise OllamaTimeoutError(
                f"Ollama request timed out after {timeout_val} seconds"
            ) from e
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e}")
            raise OllamaError(f"Ollama request failed: {e}") from e
        
        except Exception as e:
            logger.error(f"Unexpected Ollama error: {e}")
            raise OllamaError(f"Unexpected error: {e}") from e
    
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        stream: bool = False,
    ) -> str:
        """Send chat messages to Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                     [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            model: Model to use (defaults to configured model)
            temperature: Generation temperature (0.0 to 1.0)
            stream: Whether to stream response (not implemented yet)
        
        Returns:
            Generated response text
        
        Raises:
            OllamaError: If request fails
        """
        if stream:
            raise NotImplementedError("Streaming not yet implemented")
        
        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": False,
        }
        
        if temperature is not None:
            payload["options"] = {"temperature": temperature}
        
        try:
            result = await self._make_request("/api/chat", payload)
            return result.get("message", {}).get("content", "")
        
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            raise
    
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        system: str | None = None,
    ) -> str:
        """Generate text completion from prompt.
        
        Args:
            prompt: Input prompt
            model: Model to use (defaults to configured model)
            temperature: Generation temperature (0.0 to 1.0)
            system: System prompt/instructions
        
        Returns:
            Generated text
        
        Raises:
            OllamaError: If request fails
        """
        payload = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": False,
        }
        
        if system:
            payload["system"] = system
        
        if temperature is not None:
            payload["options"] = {"temperature": temperature}
        
        try:
            result = await self._make_request("/api/generate", payload)
            return result.get("response", "")
        
        except Exception as e:
            logger.error(f"Generate request failed: {e}")
            raise
    
    async def analyze_image(
        self,
        image_base64: str,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """Analyze an image using vision model.
        
        Args:
            image_base64: Base64-encoded image data
            prompt: Question or instruction about the image
            model: Vision model to use (defaults to configured vision model)
        
        Returns:
            Analysis text
        
        Raises:
            OllamaError: If request fails
        """
        # Use vision model
        vision_model = model or self.vision_model
        
        # Ollama expects messages format for vision
        messages = [
            {
                "role": "user",
                "content": prompt,
                "images": [image_base64]
            }
        ]
        
        payload = {
            "model": vision_model,
            "messages": messages,
            "stream": False,
        }
        
        try:
            result = await self._make_request(
                "/api/chat",
                payload,
                timeout=self.vision_timeout
            )
            return result.get("message", {}).get("content", "")
        
        except Exception as e:
            logger.error(f"Image analysis request failed: {e}")
            raise
    
    async def check_health(self) -> tuple[bool, str | None, list[str]]:
        """Check if Ollama is accessible and which models are available.
        
        Returns:
            (is_healthy, error_message, available_models)
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check if Ollama is running
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                
                return True, None, models
        
        except httpx.ConnectError:
            return False, f"Cannot connect to Ollama at {self.base_url}", []
        
        except httpx.TimeoutException:
            return False, "Ollama health check timed out", []
        
        except Exception as e:
            return False, f"Health check failed: {e}", []
    
    async def ensure_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available.
        
        Args:
            model_name: Model name to check
        
        Returns:
            True if model is available, False otherwise
        """
        is_healthy, error, models = await self.check_health()
        
        if not is_healthy:
            logger.warning(f"Ollama not healthy: {error}")
            return False
        
        # Check for exact match or partial match (e.g., "qwen2.5:7b" matches "qwen2.5")
        for available_model in models:
            if model_name in available_model or available_model in model_name:
                return True
        
        logger.warning(f"Model {model_name} not found. Available: {models}")
        return False


# Singleton instance
_ollama_service: OllamaService | None = None


def get_ollama_service() -> OllamaService:
    """Get or create the Ollama service singleton.
    
    Returns:
        OllamaService instance
    """
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
    return _ollama_service
