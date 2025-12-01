"""
Web search tool using Tavily API.

This provides a simple implementation of web search for entity tracking.
Replace with your preferred search provider (DuckDuckGo, Exa, etc.).
"""

from typing import List, Optional
from langchain_core.documents import Document
from datetime import datetime, timezone
import os


def search_web_tool(
    query: str,
    max_results: int = 5,
    last_days: int = 1,
    current_date: Optional[str] = None,
    **kwargs
) -> List[Document]:
    """
    Search the web for recent content related to the query.
    
    This is a simplified implementation. In production, you would:
    1. Use Tavily, Exa, or another search API
    2. Implement proper date filtering
    3. Add geographic/domain filtering as needed
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        last_days: How many days back to search
        current_date: Optional reference date
        
    Returns:
        List of Document objects with search results
    """
    try:
        # Check if Tavily is available
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        if tavily_api_key:
            from langchain_community.tools.tavily_search import TavilySearchResults
            
            tavily = TavilySearchResults(
                max_results=max_results,
                search_depth="advanced",
                include_answer=False,
                include_raw_content=True,
                include_images=False,
            )
            
            results = tavily.invoke({"query": query})
            
            # Convert to Document format
            documents = []
            for i, result in enumerate(results):
                doc = Document(
                    page_content=result.get("content", ""),
                    metadata={
                        "source_number": i + 1,
                        "url": result.get("url", ""),
                        "title": result.get("title", ""),
                        "score": result.get("score", 0.0),
                    }
                )
                documents.append(doc)
            
            return documents
        else:
            # Fallback: return empty list if no API key
            print("Warning: TAVILY_API_KEY not found. Web search disabled.")
            return []
            
    except Exception as e:
        print(f"Error in web search: {e}")
        return []

