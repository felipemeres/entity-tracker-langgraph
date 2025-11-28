"""
Unit tests for the Entity Tracker agent.
"""

import pytest
from entity_tracker.schemas import (
    EntityHistory,
    EntityHistoryEntry,
    SourceModel,
    Queries,
)
from entity_tracker.database.operations import (
    get_entity_history,
    save_entity_history_entry,
    reset_database,
)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test."""
    reset_database()


def test_save_and_retrieve_entity_history():
    """Test saving and retrieving entity history."""
    # Save an entry
    sources = [
        SourceModel(
            page_content="Test content",
            metadata={"url": "https://example.com"}
        )
    ]
    
    entry_id = save_entity_history_entry(
        entity_id="test_entity",
        content="Test event occurred",
        sources=sources,
        timestamp="2024-01-15"
    )
    
    assert entry_id is not None
    
    # Retrieve history
    history = get_entity_history("test_entity")
    assert len(history.entries) == 1
    assert history.entries[0].content == "Test event occurred"
    assert len(history.entries[0].sources) == 1


def test_multiple_entities():
    """Test tracking multiple entities independently."""
    # Save entries for two different entities
    save_entity_history_entry(
        entity_id="entity1",
        content="Entity 1 event",
        sources=[],
        timestamp="2024-01-15"
    )
    
    save_entity_history_entry(
        entity_id="entity2",
        content="Entity 2 event",
        sources=[],
        timestamp="2024-01-15"
    )
    
    # Check they're stored separately
    history1 = get_entity_history("entity1")
    history2 = get_entity_history("entity2")
    
    assert len(history1.entries) == 1
    assert len(history2.entries) == 1
    assert history1.entries[0].content == "Entity 1 event"
    assert history2.entries[0].content == "Entity 2 event"


def test_entity_history_filtering():
    """Test time-based filtering of entity history."""
    # Save entries with different timestamps
    save_entity_history_entry(
        entity_id="test_entity",
        content="Old event",
        sources=[],
        timestamp="2024-01-01T00:00:00"
    )
    
    save_entity_history_entry(
        entity_id="test_entity",
        content="Recent event",
        sources=[],
        timestamp="2024-01-15T00:00:00"
    )
    
    # Retrieve with time filter
    history = get_entity_history(
        "test_entity",
        last_hours=24,
        current_date="2024-01-15T12:00:00"
    )
    
    # Should only get the recent event
    assert len(history.entries) >= 1


def test_source_model_validation():
    """Test SourceModel Pydantic validation."""
    source = SourceModel(
        id=1,
        page_content="Test content",
        metadata={"url": "https://example.com", "title": "Test"}
    )
    
    assert source.id == 1
    assert source.page_content == "Test content"
    assert source.metadata["url"] == "https://example.com"


def test_entity_history_entry_schema():
    """Test EntityHistoryEntry schema."""
    sources = [
        SourceModel(page_content="Source 1"),
        SourceModel(page_content="Source 2")
    ]
    
    entry = EntityHistoryEntry(
        content="Test event",
        sources=sources
    )
    
    assert entry.content == "Test event"
    assert len(entry.sources) == 2


def test_queries_schema():
    """Test Queries schema."""
    queries = Queries(queries=["query 1", "query 2", "query 3"])
    
    assert len(queries.queries) == 3
    assert queries.queries[0] == "query 1"


@pytest.mark.asyncio
async def test_basic_agent_invocation():
    """Test basic agent invocation (integration test)."""
    from entity_tracker import graph
    
    result = await graph.ainvoke({
        "entity_name": "Test Entity",
        "entity_type": "organization",
        "current_date": "2024-01-15"
    })
    
    # Should complete without errors
    assert "entity_history_output" in result
    assert isinstance(result["entity_history_output"], EntityHistory)


@pytest.mark.asyncio
async def test_agent_with_relationship():
    """Test agent with relationship context."""
    from entity_tracker import graph
    
    result = await graph.ainvoke({
        "entity_name": "inflation",
        "entity_type": "concept",
        "related_entity_name": "United States",
        "related_entity_type": "location",
        "relationship_type": "affects",
        "current_date": "2024-01-15"
    })
    
    assert "entity_history_output" in result
    assert result["main_entity_name"] == "inflation"
    assert result["related_entity_name"] == "United States"

