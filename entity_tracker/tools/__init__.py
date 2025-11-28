"""Search tools for the Entity Tracker."""

from entity_tracker.tools.web_search import search_web_tool
from entity_tracker.tools.mock_tools import (
    mock_email_search,
    mock_youtube_search,
    mock_speeches_search,
    mock_scraper_search,
)

__all__ = [
    "search_web_tool",
    "mock_email_search",
    "mock_youtube_search",
    "mock_speeches_search",
    "mock_scraper_search",
]

