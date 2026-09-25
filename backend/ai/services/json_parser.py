"""Utilities for parsing JSON from AI responses.

AI models sometimes return JSON with markdown code blocks or extra text.
This module provides robust JSON extraction.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def extract_json_from_response(response: str) -> dict[str, Any]:
    """Extract and parse JSON from AI response.
    
    Handles various formats:
    - Plain JSON
    - JSON in markdown code blocks (```json ... ```)
    - JSON with surrounding text
    
    Args:
        response: AI response text
    
    Returns:
        Parsed JSON dict
    
    Raises:
        ValueError: If no valid JSON found
    """
    # Try direct parsing first
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass
    
    # Try extracting from markdown code block
    json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(json_pattern, response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try finding JSON object in text
    # Look for outermost { ... }
    brace_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
    matches = re.findall(brace_pattern, response, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # Last resort: try to find anything between { and }
    start = response.find("{")
    end = response.rfind("}")
    
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(response[start:end + 1])
        except json.JSONDecodeError:
            pass
    
    logger.error(f"Failed to extract JSON from response: {response[:200]}...")
    raise ValueError("No valid JSON found in AI response")


def validate_json_structure(
    data: dict[str, Any],
    required_fields: list[str],
) -> tuple[bool, str]:
    """Validate that JSON has required fields.
    
    Args:
        data: Parsed JSON data
        required_fields: List of required field names
    
    Returns:
        (is_valid, error_message)
    """
    missing = [field for field in required_fields if field not in data]
    
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    return True, ""


def safe_json_parse(
    response: str,
    default: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Safely parse JSON with fallback to default.
    
    Args:
        response: AI response text
        default: Default value if parsing fails (empty dict if None)
    
    Returns:
        Parsed JSON or default
    """
    try:
        return extract_json_from_response(response)
    except ValueError as e:
        logger.warning(f"JSON parsing failed: {e}")
        return default if default is not None else {}
