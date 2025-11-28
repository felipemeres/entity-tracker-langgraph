"""Simplified database operations for the Entity Tracker."""

from entity_tracker.database.operations import (
    get_entity_history,
    save_entity_history_entry,
)

__all__ = [
    "get_entity_history",
    "save_entity_history_entry",
]

