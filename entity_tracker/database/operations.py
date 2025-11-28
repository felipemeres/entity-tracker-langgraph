"""
Simplified database operations for entity tracking.

This is a mock implementation that stores data in memory.
In a production environment, replace this with actual database operations.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from entity_tracker.schemas import EntityHistory, EntityHistoryEntry, SourceModel

# In-memory storage for demonstration
_entity_histories: Dict[str, List[Dict[str, Any]]] = {}
_entity_sources: Dict[int, SourceModel] = {}
_source_counter = 0


def get_entity_history(
    entity_id: str,
    last_hours: Optional[int] = None,
    current_date: Optional[str] = None,
    limit: int = 100
) -> EntityHistory:
    """
    Retrieve entity history from the database.
    
    Args:
        entity_id: The entity identifier
        last_hours: Optional time window in hours
        current_date: Optional reference date
        limit: Maximum number of entries to return
        
    Returns:
        EntityHistory object with historical entries
    """
    if entity_id not in _entity_histories:
        return EntityHistory(entries=[])
    
    entries = _entity_histories[entity_id]
    
    # Apply time filtering if specified
    if last_hours and current_date:
        try:
            ref_date = datetime.fromisoformat(current_date)
            cutoff_date = ref_date - timedelta(hours=last_hours)
            
            filtered_entries = []
            for entry in entries:
                entry_date = datetime.fromisoformat(entry["timestamp"])
                if entry_date >= cutoff_date:
                    filtered_entries.append(entry)
            entries = filtered_entries
        except:
            pass  # If date parsing fails, return all entries
    
    # Apply limit
    entries = entries[:limit]
    
    # Convert to EntityHistory format
    history_entries = []
    for entry in entries:
        sources = [
            SourceModel(
                id=src.get("id"),
                page_content=src.get("page_content", ""),
                metadata=src.get("metadata", {}),
                created_at=src.get("created_at")
            )
            for src in entry.get("sources", [])
        ]
        
        history_entries.append(
            EntityHistoryEntry(
                content=entry["content"],
                sources=sources
            )
        )
    
    return EntityHistory(entries=history_entries)


def save_entity_history_entry(
    entity_id: str,
    content: str,
    sources: List[SourceModel],
    timestamp: Optional[str] = None,
    relationship_id: Optional[str] = None
) -> int:
    """
    Save a new entity history entry to the database.
    
    Args:
        entity_id: The entity identifier
        content: The history entry content
        sources: List of source documents supporting this entry
        timestamp: Optional timestamp for the entry
        relationship_id: Optional relationship context
        
    Returns:
        The ID of the saved entry
    """
    global _source_counter
    
    if entity_id not in _entity_histories:
        _entity_histories[entity_id] = []
    
    # Convert sources to dict format for storage
    source_dicts = []
    for source in sources:
        _source_counter += 1
        source_dict = {
            "id": _source_counter,
            "page_content": source.page_content,
            "metadata": source.metadata,
            "created_at": source.created_at or datetime.now().isoformat()
        }
        source_dicts.append(source_dict)
        _entity_sources[_source_counter] = source
    
    entry = {
        "content": content,
        "sources": source_dicts,
        "timestamp": timestamp or datetime.now().isoformat(),
        "relationship_id": relationship_id
    }
    
    _entity_histories[entity_id].insert(0, entry)  # Add to front (most recent)
    
    return len(_entity_histories[entity_id])


def reset_database():
    """Reset the in-memory database. Useful for testing."""
    global _entity_histories, _entity_sources, _source_counter
    _entity_histories = {}
    _entity_sources = {}
    _source_counter = 0

