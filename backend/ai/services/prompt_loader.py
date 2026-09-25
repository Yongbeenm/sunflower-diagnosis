"""Utility for loading prompt templates."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from file.
    
    Args:
        prompt_name: Name of prompt file (without .txt extension)
    
    Returns:
        Prompt text
    
    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    prompt_path = PROMPTS_DIR / f"{prompt_name}.txt"
    
    if not prompt_path.exists():
        logger.error(f"Prompt file not found: {prompt_path}")
        raise FileNotFoundError(f"Prompt template '{prompt_name}' not found")
    
    try:
        return prompt_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read prompt {prompt_name}: {e}")
        raise


def format_prompt(template: str, **kwargs: str) -> str:
    """Format a prompt template with variables.
    
    Args:
        template: Prompt template string
        **kwargs: Variables to substitute
    
    Returns:
        Formatted prompt
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.error(f"Missing template variable: {e}")
        raise ValueError(f"Missing required template variable: {e}") from e
