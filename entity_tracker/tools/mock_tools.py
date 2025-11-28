"""
Mock search tools for demonstration purposes.

In a production environment, replace these with actual integrations to:
- Email/Gmail APIs
- YouTube transcript services
- Speech databases
- Web scraping services
"""

from typing import List
from langchain.schema import Document
from datetime import datetime, timezone


def mock_email_search(
    query: str,
    max_results: int = 10,
    last_hours: int = 24,
    **kwargs
) -> List[Document]:
    """
    Mock email search function.
    
    In production, this would search Gmail or other email providers.
    """
    # Return empty for demo - replace with actual email search
    return []


def mock_youtube_search(
    query: str,
    max_results: int = 5,
    last_days: int = 1,
    **kwargs
) -> List[Document]:
    """
    Mock YouTube search function.
    
    In production, this would search YouTube transcripts via an API.
    """
    # Return empty for demo - replace with actual YouTube search
    return []


def mock_speeches_search(
    query: str,
    max_results: int = 5,
    **kwargs
) -> List[Document]:
    """
    Mock speeches database search function.
    
    In production, this would search a vectorstore of speeches.
    """
    # Return empty for demo - replace with actual speech database search
    return []


def mock_scraper_search(
    query: str,
    max_results: int = 10,
    last_hours: int = 72,
    **kwargs
) -> List[Document]:
    """
    Mock scraper search function.
    
    In production, this would search scraped web content from a database.
    """
    # Return empty for demo - replace with actual scraper search
    return []

