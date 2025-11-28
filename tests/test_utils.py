"""Tests for utility functions."""

import pytest
from langchain.schema import Document
from entity_tracker.utils.sources import parse_and_cap_source_content, parse_and_cap_sources


def test_parse_and_cap_source_content():
    """Test source content capping."""
    # Create a document with long content
    long_content = "A" * 5000
    doc = Document(page_content=long_content, metadata={})
    
    # Cap to 4000 characters
    capped = parse_and_cap_source_content(doc, max_length=4000)
    
    assert len(capped) <= 4003  # 4000 + "..."
    assert capped.endswith("...")


def test_parse_and_cap_source_content_short():
    """Test that short content is not modified."""
    short_content = "Short content"
    doc = Document(page_content=short_content, metadata={})
    
    capped = parse_and_cap_source_content(doc, max_length=4000)
    
    assert capped == short_content


def test_parse_and_cap_sources_list():
    """Test capping multiple sources."""
    docs = [
        Document(page_content="A" * 5000, metadata={"id": 1}),
        Document(page_content="B" * 5000, metadata={"id": 2}),
        Document(page_content="Short", metadata={"id": 3}),
    ]
    
    capped = parse_and_cap_sources(docs, max_length=4000)
    
    assert len(capped) == 3
    assert len(capped[0].page_content) <= 4003
    assert len(capped[1].page_content) <= 4003
    assert capped[2].page_content == "Short"


def test_parse_and_cap_sources_empty():
    """Test with empty list."""
    capped = parse_and_cap_sources([], max_length=4000)
    assert capped == []


def test_parse_and_cap_sources_preserves_metadata():
    """Test that metadata is preserved during capping."""
    docs = [
        Document(
            page_content="A" * 5000,
            metadata={"url": "https://example.com", "title": "Test"}
        )
    ]
    
    capped = parse_and_cap_sources(docs, max_length=4000)
    
    assert capped[0].metadata["url"] == "https://example.com"
    assert capped[0].metadata["title"] == "Test"

