"""
Pydantic schemas for the Entity Tracker agent.

These schemas define the structured data models used throughout the entity tracking pipeline.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Queries(BaseModel):
    """Search queries for entity research."""
    queries: List[str] = Field(
        description="The queries to search for the entity.",
    )


class SourcesReview(BaseModel):
    """Review results indicating which sources to keep."""
    sources_to_keep: List[int] = Field(
        description="The source numbers to keep.",
    )


class SourceModel(BaseModel):
    """A source document with metadata."""
    id: Optional[int] = None
    page_content: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None


class EntityHistoryEntry(BaseModel):
    """A single entry in an entity's timeline."""
    content: str = Field(
        description="The content of the entry.",
    )
    sources: List[SourceModel] = Field(
        description="The sources of the entry.",
        default_factory=list
    )


class EntityHistory(BaseModel):
    """The complete history timeline for an entity."""
    entries: List[EntityHistoryEntry] = Field(
        description="Entries in the history of the entity.",
        default_factory=list
    )


class EntityHistoryPlan(BaseModel):
    """A plan for creating a history entry."""
    event: str = Field(
        description="The event that has occurred.",
    )
    reasoning: str = Field(
        description="The reasoning for why the event is important.",
    )
    source_numbers: List[int] = Field(
        description="The source numbers that support the event.",
    )


class ShouldWriteHistoryEntries(BaseModel):
    """Decision on whether to write history entries."""
    entity_history_plans: List[EntityHistoryPlan] = Field(
        description="The entity history plans to write.",
        default_factory=list
    )


class NewEntityHistoryEntry(BaseModel):
    """A new entry to be added to entity history."""
    content: str = Field(
        description="The content of the history entry.",
    )


class ShouldUpdateEntityHistory(BaseModel):
    """Decision on which history entries to update."""
    entity_history_entries: List[int] = Field(
        description="The numbers of the entity history entries to update.",
        default_factory=list
    )

