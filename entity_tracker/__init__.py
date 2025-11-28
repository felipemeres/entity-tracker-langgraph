"""
Entity Tracker - A LangGraph-based entity monitoring and history tracking system.

This package provides comprehensive entity tracking capabilities including:
- Multi-source research (web, email, YouTube, speeches, scraper)
- Intelligent query generation and source review
- Timeline curation with factual development tracking
- Entity relationship management
"""

__version__ = "1.0.0"

from entity_tracker.agent import graph

__all__ = ["graph"]

