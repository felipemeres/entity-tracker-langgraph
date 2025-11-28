"""
Utility functions for processing and managing source documents.

This module provides utilities for content truncation, source parsing, and deduplication.
"""

from langchain.schema import Document
from typing import List


def parse_and_cap_source_content(source: Document, max_length: int = 4000) -> str:
    """
    Parse and cap the content length of a source to a specified maximum length.
    
    Args:
        source: A source object (Document or SourceModel)
        max_length: Maximum character length for the content (default: 4000)
        
    Returns:
        str: The parsed and capped content
    """
    if not source:
        return ""
        
    # Get content from either page_content or content attribute
    content = getattr(source, "page_content", None) or getattr(source, "content", "")
    
    if not content:
        return ""
        
    # If content is longer than max_length, truncate it
    if len(content) > max_length:
        # Try to find a good breaking point (end of sentence or paragraph)
        break_chars = ['. ', '! ', '? ', '\n\n']
        break_point = max_length
        
        # Look for the last occurrence of any break character before max_length
        for char in break_chars:
            last_break = content[:max_length].rfind(char)
            if last_break != -1 and last_break > break_point - 100:  # Only use if not too far back
                break_point = last_break + len(char)
                
        content = content[:break_point].strip() + "..."
        
    return content


def parse_and_cap_sources(sources: List, max_length: int = 4000) -> List:
    """
    Parse and cap the content length of multiple sources.
    
    Args:
        sources: List of source objects (Document or SourceModel)
        max_length: Maximum character length for each source's content (default: 4000)
        
    Returns:
        list: List of sources with capped content
    """
    if not sources:
        return []
        
    parsed_sources = []
    for source in sources:
        # Get the content from either page_content or content attribute
        content = getattr(source, "page_content", None) or getattr(source, "content", "")
        
        # Parse and cap the content
        capped_content = parse_and_cap_source_content(source, max_length)
        
        # Create a new Document with the capped content
        if isinstance(source, Document):
            parsed_source = Document(
                page_content=capped_content,
                metadata=source.metadata.copy() if source.metadata else {}
            )
        else:
            # For other types, create a new instance and copy all attributes
            parsed_source = type(source)()
            for attr in dir(source):
                if not attr.startswith('__'):
                    try:
                        setattr(parsed_source, attr, getattr(source, attr))
                    except:
                        pass
            
            # Update the content with the capped version
            if hasattr(parsed_source, 'page_content'):
                parsed_source.page_content = capped_content
            elif hasattr(parsed_source, 'content'):
                parsed_source.content = capped_content
            
        parsed_sources.append(parsed_source)
        
    return parsed_sources

