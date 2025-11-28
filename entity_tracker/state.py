"""
State management for the Entity Tracker graph.

Defines the state structure that flows through the LangGraph nodes.
"""

from typing import Optional, Annotated
from typing_extensions import TypedDict
from langchain.schema import Document
from entity_tracker.schemas import EntityHistory, EntityHistoryPlan


def extend_field(existing: list, update: list | str):
    """Reducer function for extending list fields in state."""
    if update == "DELETE":
        return []
    return (existing or []) + update


class EntityTrackerInput(TypedDict):
    """Input parameters for the entity tracker."""
    entity_name: Optional[str]
    entity_id: Optional[str]
    entity_type: Optional[str]
    related_entity_name: Optional[str]
    related_entity_type: Optional[str]
    relationship_type: Optional[str]
    entity_relationship_id: Optional[str]
    graph_settings: Optional[dict]
    current_date: Optional[str]


class EntityTrackerState(EntityTrackerInput):
    """The complete state for the entity tracker workflow."""
    queries: list[str]
    web_sources: list[Document]
    email_sources: list[Document]
    youtube_sources: list[Document]
    speeches_sources: list[Document]
    scraper_sources: list[Document]
    sources: list[Document]
    entity_history: EntityHistory
    entity_history_without_sources: EntityHistory
    entity_history_plans: list[EntityHistoryPlan]
    entity_history_entries: Annotated[list, extend_field]
    entity_history_entries_filtered: list
    no_new_information: bool
    related_entity_id: Optional[int]
    relationship_type_id: Optional[int]
    main_entity_name: Optional[str]
    entity_history_output: Optional[EntityHistory]


class EntityTrackerOutput(TypedDict):
    """Output from the entity tracker."""
    entity_history_output: EntityHistory
    no_new_information: bool

