"""
Helper Functions Module
Contains utility functions used across the application
"""
import re
import requests


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and normalizing spaces.
    
    Args:
        text: Raw text to clean
    
    Returns:
        Cleaned text with normalized whitespace
    
    Example:
        >>> clean_text("Hello    World\\n\\n  Test")
        'Hello World Test'
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    return text.strip()


def setup_session() -> requests.Session:
    """
    Create and configure a requests Session with appropriate headers.
    
    Returns:
        Configured requests.Session object
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    return session


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    
    Args:
        url: URL string to validate
    
    Returns:
        True if valid URL, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None