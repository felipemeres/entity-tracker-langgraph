"""
Configuration for the Entity Tracker agent.

This module defines all configurable parameters for the entity tracking workflow.
"""

import os
from dataclasses import dataclass, field, fields
from typing import Any, Optional
from langchain_core.runnables import RunnableConfig

from entity_tracker.prompts import (
    universal_query_writer_system_instructions,
    web_query_writer_system_instructions,
    email_query_writer_system_instructions,
    youtube_query_writer_system_instructions,
    speeches_query_writer_system_instructions,
    scraper_query_writer_system_instructions,
    sources_review_system_instructions,
    should_write_history_entry_system_instructions,
    should_update_entity_history_system_instructions,
)


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the Entity Tracker agent."""
    
    # LLM Configuration
    # Complexity: 1 - Query generation (simple, structured output)
    llm_query_creator: str = "openai/gpt-4o-mini"
    llm_query_creator_fallback_model: str = "openai/gpt-3.5-turbo"
    llm_query_creator_temperature: float = 0.0
    
    # Complexity: 2 - Source review and evaluation (moderate reasoning)
    llm_reviewer: str = "openai/gpt-4o"
    llm_reviewer_fallback_model: str = "openai/gpt-4o-mini"
    llm_reviewer_temperature: float = 0.0
    
    # Complexity: 3 - Timeline writing (requires sophisticated judgment)
    llm_writer: str = "openai/gpt-4o"
    llm_writer_fallback_model: str = "openai/gpt-4o-mini"
    llm_writer_temperature: float = 0.0
    
    # Graph configuration
    user_id: str = "system"
    last_hours: int = 24
    entity_history_entry_limit: int = 100
    entity_history_last_hours: int = 720  # 30 days
    update_entity_metadata: bool = False
    debug: bool = False
    
    # Source content configuration
    source_content_max_length: int = 8000  # Maximum length for source content before truncation
    
    # Query generation
    create_universal_queries_enabled: bool = False
    create_queries_pass_sources: bool = False
    universal_queries_number_of_queries: int = 2
    
    # Search configuration - Web
    search_web_enabled: bool = True
    search_web_create_queries_enabled: bool = False
    search_web_last_days: int = 1
    search_web_max_results: int = 5
    search_web_number_of_queries: int = 2
    search_web_timeout: int = 300
    search_web_last_hours: int = 24
    search_web_country_rank_enabled: bool = False
    search_web_country_rank: int = 100

    # Search configuration - Email
    search_email_enabled: bool = False
    search_email_create_queries_enabled: bool = False
    search_email_last_days: int = 1
    search_email_max_results: int = 10
    search_email_number_of_queries: int = 2
    search_email_last_hours: int = 24
    search_email_timeout: int = 300
    
    # Search configuration - YouTube
    search_youtube_enabled: bool = False
    search_youtube_create_queries_enabled: bool = False
    search_youtube_last_days: int = 1
    search_youtube_max_results: int = 5
    search_youtube_number_of_queries: int = 2
    search_youtube_last_hours: int = 24
    search_youtube_timeout: int = 300
    
    # Search configuration - Speeches
    search_speeches_enabled: bool = False
    search_speeches_create_queries_enabled: bool = False
    search_speeches_last_days: int = 1
    search_speeches_max_results: int = 5
    search_speeches_number_of_queries: int = 2
    search_speeches_last_hours: int = 24
    search_speeches_timeout: int = 300
    
    # Search configuration - Scraper
    search_scraper_enabled: bool = False
    search_scraper_create_queries_enabled: bool = False
    search_scraper_last_hours: int = 72  # 3 days
    search_scraper_max_results: int = 10
    search_scraper_number_of_queries: int = 2
    search_scraper_timeout: int = 300
    review_scraper_sources_enabled: bool = True
    
    # Prompt configuration - Should Pass Sources
    create_queries_pass_previous_entries_sources: bool = False
    review_sources_pass_previous_entries_sources: bool = False
    should_write_history_entry_pass_previous_entries_sources: bool = False
    write_history_entry_pass_previous_entries_sources: bool = False
    should_update_entity_history_pass_previous_entries_sources: bool = False
    
    # Prompts
    universal_query_writer_system_instructions: str = universal_query_writer_system_instructions
    web_query_writer_system_instructions: str = web_query_writer_system_instructions
    email_query_writer_system_instructions: str = email_query_writer_system_instructions
    youtube_query_writer_system_instructions: str = youtube_query_writer_system_instructions
    speeches_query_writer_system_instructions: str = speeches_query_writer_system_instructions
    scraper_query_writer_system_instructions: str = scraper_query_writer_system_instructions
    sources_review_system_instructions: str = sources_review_system_instructions
    should_write_history_entry_system_instructions: str = should_write_history_entry_system_instructions
    should_update_entity_history_system_instructions: str = should_update_entity_history_system_instructions
    
    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})

