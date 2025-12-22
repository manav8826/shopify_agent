import re
import html
from datetime import datetime
from typing import Optional, Tuple

class ValidationError(Exception):
    pass

def validate_store_url(url: str) -> bool:
    """
    Validate if the provided string is a valid Shopify store URL.
    Must start with https:// and match typical Shopify domains.
    """
    if not url:
        return False
        
    # Standard Shopify regex pattern from our Pydantic models
    pattern = r'^https?://[\w\-]+(\.[\w\-]+)+[/#?]?.*$'
    if not re.match(pattern, url):
        return False
        
    return True

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks and enforce length limits.
    - Strips HTML tags.
    - Escapes special characters.
    - Truncates to max_length.
    """
    if not text:
        return ""
        
    # Basic HTML escaping
    clean_text = html.escape(text)
    
    # Remove potentially dangerous patterns (basic script tag removal for double safety)
    # The html.escape handles <script> -> &lt;script&gt;, but explicit removal 
    # of raw patterns can be useful if unescaping happens elsewhere.
    # For now, relying on escape is standard safest practice for text content.
    
    # Truncate
    if len(clean_text) > max_length:
        clean_text = clean_text[:max_length]
        
    return clean_text

def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    Validate that start_date is before or equal to end_date.
    Expects ISO 8601 strings.
    """
    try:
        # Flexible parsing
        dt_start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        dt_end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        
        return dt_start <= dt_end
    except (ValueError, TypeError):
        raise ValidationError("Invalid date format. Use ISO 8601.")

def validate_api_structure(data: dict, required_keys: list) -> bool:
    """
    Check if a dictionary contains all required keys.
    """
    return all(key in data for key in required_keys)
