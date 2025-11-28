"""
Entity Tracker LangGraph Agent - Main Graph Implementation

This module contains the core LangGraph workflow for entity tracking,
including entity initialization, multi-source search, source review,
and timeline curation.
"""

from typing import Literal
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.pregel import RetryPolicy
from langgraph.types import Command
from langchain.schema import Document

from entity_tracker.configuration import Configuration
from entity_tracker.state import (
    EntityTrackerInput,
    EntityTrackerState,
    EntityTrackerOutput,
)
from entity_tracker.schemas import (
    Queries,
    SourcesReview,
    EntityHistory,
    EntityHistoryEntry,
    SourceModel,
    ShouldWriteHistoryEntries,
    ShouldUpdateEntityHistory,
)
from entity_tracker.utils import (
    create_llm_configs,
    create_llm_from_config,
    parse_and_cap_sources,
)
from entity_tracker.tools import (
    search_web_tool,
    mock_email_search,
    mock_youtube_search,
    mock_speeches_search,
    mock_scraper_search,
)
from entity_tracker.database import (
    get_entity_history,
    save_entity_history_entry,
)


async def initialize_search(state: EntityTrackerInput, config: RunnableConfig):
    """Initialize the search by setting up entity context and retrieving history."""
    configurable = Configuration.from_runnable_config(config)
    
    # Validate and set current date
    if state.get("current_date"):
        current_date = state.get("current_date")
        try:
            datetime.strptime(current_date, "%Y-%m-%d")
        except ValueError:
            if configurable.debug:
                print(f"Invalid date format: {current_date}. Using current date.")
            current_date = datetime.now().strftime("%Y-%m-%d")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Get entity information
    entity_name = state.get("entity_name", "")
    entity_id = state.get("entity_id", entity_name)  # Use name as ID if not provided
    
    # Construct full entity name with relationship context if provided
    related_entity_name = state.get("related_entity_name")
    if related_entity_name:
        full_entity_name = f"{entity_name} in {related_entity_name}"
    else:
        full_entity_name = entity_name
    
    # Retrieve existing entity history
    last_hours = configurable.entity_history_last_hours
    entity_history = get_entity_history(
        entity_id=entity_id,
        last_hours=last_hours,
        current_date=current_date,
        limit=configurable.entity_history_entry_limit
    )
    
    # Create version without sources for prompts that don't need them
    entity_history_without_sources = EntityHistory(
        entries=[
            EntityHistoryEntry(content=entry.content, sources=[])
            for entry in entity_history.entries
        ]
    )
    
    # Get graph settings (custom queries, prompts, etc.)
    graph_settings = state.get("graph_settings", {})
    
    return {
        "entity_history": entity_history,
        "entity_history_without_sources": entity_history_without_sources,
        "entity_id": entity_id,
        "entity_name": full_entity_name,
        "main_entity_name": entity_name,
        "related_entity_name": related_entity_name,
        "graph_settings": graph_settings,
        "current_date": current_date
    }


async def create_universal_queries(state: EntityTrackerState, config: RunnableConfig):
    """Create universal search queries for the entity."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.create_universal_queries_enabled:
        return {"queries": []}
    
    llm_configs = create_llm_configs(configurable)
    llm_query_creator = await create_llm_from_config(llm_configs["llm_query_creator"], Queries)
    
    entity_history = (state["entity_history"] if configurable.create_queries_pass_previous_entries_sources 
                     else state["entity_history_without_sources"])
    
    # Start with base queries
    queries_list = [state.get("entity_name")]
    
    # Add any custom queries from graph settings
    if state.get("graph_settings"):
        search_queries = state.get("graph_settings").get("search_queries", [])
        queries_list.extend(search_queries)
    
    # Generate additional queries
    queries = await llm_query_creator.ainvoke([
        SystemMessage(content=configurable.universal_query_writer_system_instructions.format(
            entity=state.get("entity_name"),
            number_of_queries=configurable.universal_queries_number_of_queries,
            current_date=state.get("current_date"),
            queries=queries_list,
            entity_history=entity_history
        )),
        HumanMessage(content="Please return a list of queries.")
    ])
    
    queries_list.extend(queries.queries[:configurable.universal_queries_number_of_queries])
    
    return {"queries": queries_list}


async def search_web(state: EntityTrackerState, config: RunnableConfig):
    """Search the web for entity-related content."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.search_web_enabled:
        return {"web_sources": []}
    
    queries_list = state.get("queries", [state.get("entity_name")])
    sources = []
    
    for query in queries_list:
        results = search_web_tool(
            query=query,
            max_results=configurable.search_web_max_results,
            last_days=configurable.search_web_last_days,
            current_date=state.get("current_date"),
        )
        sources.extend(results)
    
    # Add source numbers
    for i, source in enumerate(sources):
        if source.metadata is None:
            source.metadata = {}
        source.metadata["source_number"] = i + 1
    
    # Cap source content length
    capped_sources = parse_and_cap_sources(sources, max_length=configurable.source_content_max_length)
    
    return {"web_sources": capped_sources}


async def review_web_sources(state: EntityTrackerState, config: RunnableConfig):
    """Review web sources and filter for relevance."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.search_web_enabled or not state.get("web_sources"):
        return {"web_sources": []}
    
    llm_configs = create_llm_configs(configurable)
    llm_reviewer = await create_llm_from_config(llm_configs["llm_reviewer"], SourcesReview)
    
    entity_history = (state["entity_history"] if configurable.review_sources_pass_previous_entries_sources
                     else state["entity_history_without_sources"])
    
    review_result = await llm_reviewer.ainvoke([
        SystemMessage(content=configurable.sources_review_system_instructions.format(
            entity=state.get("entity_name"),
            current_date=state.get("current_date"),
            sources=state["web_sources"],
            last_hours=configurable.search_web_last_hours,
            entity_history=entity_history
        )),
        HumanMessage(content="Please review the sources and return numbers to keep.")
    ])
    
    sources_to_keep = review_result.sources_to_keep
    sources = [source for i, source in enumerate(state["web_sources"]) if i + 1 in sources_to_keep]
    
    return {"web_sources": sources}


async def search_email(state: EntityTrackerState, config: RunnableConfig):
    """Search email for entity-related content."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.search_email_enabled:
        return {"email_sources": []}
    
    queries_list = state.get("queries", [state.get("entity_name")])
    sources = []
    
    for query in queries_list:
        results = mock_email_search(
            query=query,
            max_results=configurable.search_email_max_results,
            last_hours=configurable.search_email_last_hours,
        )
        sources.extend(results)
    
    # Add source numbers and cap content
    for i, source in enumerate(sources):
        if source.metadata is None:
            source.metadata = {}
        source.metadata["source_number"] = i + 1
    
    capped_sources = parse_and_cap_sources(sources, max_length=configurable.source_content_max_length)
    return {"email_sources": capped_sources}


async def review_email_sources(state: EntityTrackerState, config: RunnableConfig):
    """Review email sources for relevance."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.search_email_enabled or not state.get("email_sources"):
        return {"email_sources": []}
    
    llm_configs = create_llm_configs(configurable)
    llm_reviewer = await create_llm_from_config(llm_configs["llm_reviewer"], SourcesReview)
    
    entity_history = (state["entity_history"] if configurable.review_sources_pass_previous_entries_sources
                     else state["entity_history_without_sources"])
    
    review_result = await llm_reviewer.ainvoke([
        SystemMessage(content=configurable.sources_review_system_instructions.format(
            entity=state.get("entity_name"),
            current_date=state.get("current_date"),
            sources=state["email_sources"],
            last_hours=configurable.search_email_last_hours,
            entity_history=entity_history
        )),
        HumanMessage(content="Please review the sources.")
    ])
    
    sources_to_keep = review_result.sources_to_keep
    sources = [source for i, source in enumerate(state["email_sources"]) if i + 1 in sources_to_keep]
    
    return {"email_sources": sources}


async def search_youtube(state: EntityTrackerState, config: RunnableConfig):
    """Search YouTube for entity-related content."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.search_youtube_enabled:
        return {"youtube_sources": []}
    
    queries_list = state.get("queries", [state.get("entity_name")])
    sources = []
    
    for query in queries_list:
        results = mock_youtube_search(
            query=query,
            max_results=configurable.search_youtube_max_results,
            last_days=configurable.search_youtube_last_days,
        )
        sources.extend(results)
    
    for i, source in enumerate(sources):
        if source.metadata is None:
            source.metadata = {}
        source.metadata["source_number"] = i + 1
    
    capped_sources = parse_and_cap_sources(sources, max_length=configurable.source_content_max_length)
    return {"youtube_sources": capped_sources}


async def review_youtube_sources(state: EntityTrackerState, config: RunnableConfig):
    """Review YouTube sources for relevance."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.search_youtube_enabled or not state.get("youtube_sources"):
        return {"youtube_sources": []}
    
    llm_configs = create_llm_configs(configurable)
    llm_reviewer = await create_llm_from_config(llm_configs["llm_reviewer"], SourcesReview)
    
    entity_history = (state["entity_history"] if configurable.review_sources_pass_previous_entries_sources
                     else state["entity_history_without_sources"])
    
    review_result = await llm_reviewer.ainvoke([
        SystemMessage(content=configurable.sources_review_system_instructions.format(
            entity=state.get("entity_name"),
            current_date=state.get("current_date"),
            sources=state["youtube_sources"],
            last_hours=configurable.search_youtube_last_hours,
            entity_history=entity_history
        )),
        HumanMessage(content="Please review the sources.")
    ])
    
    sources_to_keep = review_result.sources_to_keep
    sources = [source for i, source in enumerate(state["youtube_sources"]) if i + 1 in sources_to_keep]
    
    return {"youtube_sources": sources}


async def search_speeches(state: EntityTrackerState, config: RunnableConfig):
    """Search speeches database for entity-related content."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.search_speeches_enabled:
        return {"speeches_sources": []}
    
    queries_list = state.get("queries", [state.get("entity_name")])
    sources = []
    
    for query in queries_list:
        results = mock_speeches_search(
            query=query,
            max_results=configurable.search_speeches_max_results,
        )
        sources.extend(results)
    
    for i, source in enumerate(sources):
        if source.metadata is None:
            source.metadata = {}
        source.metadata["source_number"] = i + 1
    
    capped_sources = parse_and_cap_sources(sources, max_length=configurable.source_content_max_length)
    return {"speeches_sources": capped_sources}


async def review_speeches_sources(state: EntityTrackerState, config: RunnableConfig):
    """Review speeches sources for relevance."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.search_speeches_enabled or not state.get("speeches_sources"):
        return {"speeches_sources": []}
    
    llm_configs = create_llm_configs(configurable)
    llm_reviewer = await create_llm_from_config(llm_configs["llm_reviewer"], SourcesReview)
    
    entity_history = (state["entity_history"] if configurable.review_sources_pass_previous_entries_sources
                     else state["entity_history_without_sources"])
    
    review_result = await llm_reviewer.ainvoke([
        SystemMessage(content=configurable.sources_review_system_instructions.format(
            entity=state.get("entity_name"),
            current_date=state.get("current_date"),
            sources=state["speeches_sources"],
            last_hours=configurable.search_speeches_last_hours,
            entity_history=entity_history
        )),
        HumanMessage(content="Please review the sources.")
    ])
    
    sources_to_keep = review_result.sources_to_keep
    sources = [source for i, source in enumerate(state["speeches_sources"]) if i + 1 in sources_to_keep]
    
    return {"speeches_sources": sources}


async def search_scraper(state: EntityTrackerState, config: RunnableConfig):
    """Search scraper database for entity-related content."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.search_scraper_enabled:
        return {"scraper_sources": []}
    
    queries_list = state.get("queries", [state.get("entity_name")])
    sources = []
    
    for query in queries_list:
        results = mock_scraper_search(
            query=query,
            max_results=configurable.search_scraper_max_results,
            last_hours=configurable.search_scraper_last_hours,
        )
        sources.extend(results)
    
    for i, source in enumerate(sources):
        if source.metadata is None:
            source.metadata = {}
        source.metadata["source_number"] = i + 1
    
    capped_sources = parse_and_cap_sources(sources, max_length=configurable.source_content_max_length)
    return {"scraper_sources": capped_sources}


async def review_scraper_sources(state: EntityTrackerState, config: RunnableConfig):
    """Review scraper sources for relevance."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.search_scraper_enabled or not configurable.review_scraper_sources_enabled:
        return {"scraper_sources": state.get("scraper_sources", [])}
    
    if not state.get("scraper_sources"):
        return {"scraper_sources": []}
    
    llm_configs = create_llm_configs(configurable)
    llm_reviewer = await create_llm_from_config(llm_configs["llm_reviewer"], SourcesReview)
    
    entity_history = (state["entity_history"] if configurable.review_sources_pass_previous_entries_sources
                     else state["entity_history_without_sources"])
    
    review_result = await llm_reviewer.ainvoke([
        SystemMessage(content=configurable.sources_review_system_instructions.format(
            entity=state.get("entity_name"),
            current_date=state.get("current_date"),
            sources=state["scraper_sources"],
            last_hours=configurable.search_scraper_last_hours,
            entity_history=entity_history
        )),
        HumanMessage(content="Please review the sources.")
    ])
    
    sources_to_keep = review_result.sources_to_keep
    sources = [source for i, source in enumerate(state["scraper_sources"]) if i + 1 in sources_to_keep]
    
    return {"scraper_sources": sources}


async def gather_sources(state: EntityTrackerState, config: RunnableConfig):
    """Consolidate and deduplicate sources from all search types."""
    # Combine all sources
    sources = (state.get("web_sources", []) + 
               state.get("email_sources", []) + 
               state.get("youtube_sources", []) + 
               state.get("speeches_sources", []) + 
               state.get("scraper_sources", []))
    
    if not sources:
        return {"sources": []}
    
    # Convert Document objects to SourceModel
    source_models = []
    for source in sources:
        if isinstance(source, Document):
            source_id = source.metadata.get("source_number") if source.metadata else None
            source_models.append(SourceModel(
                id=source_id,
                page_content=source.page_content,
                metadata=source.metadata
            ))
        else:
            source_models.append(source)
    
    # Deduplicate based on URL/link
    unique_sources = []
    seen_urls = set()
    seen_links = set()
    
    for source in source_models:
        should_include = True
        
        if source.metadata and "url" in source.metadata:
            url = source.metadata["url"]
            if url in seen_urls:
                should_include = False
            else:
                seen_urls.add(url)
        
        if should_include and source.metadata and "link" in source.metadata:
            link = source.metadata["link"]
            if link in seen_links:
                should_include = False
            else:
                seen_links.add(link)
        
        if should_include:
            unique_sources.append(source)
    
    # Re-number sources
    for i, source in enumerate(unique_sources):
        if source.metadata is None:
            source.metadata = {}
        source.metadata["source_number"] = i + 1
        source.id = i + 1
    
    return {
        "sources": unique_sources,
        "web_sources": [],
        "email_sources": [],
        "youtube_sources": [],
        "speeches_sources": [],
        "scraper_sources": []
    }


async def should_write_history_entry(state: EntityTrackerState, config: RunnableConfig):
    """Determine if new history entries should be written."""
    if not state.get("sources"):
        return [
            Send("update_entity_history", {
                "entity_history_entries": [],
                "no_new_information": True
            })
        ]
    
    configurable = Configuration.from_runnable_config(config)
    
    llm_configs = create_llm_configs(configurable)
    llm_reviewer = await create_llm_from_config(llm_configs["llm_reviewer"], ShouldWriteHistoryEntries)
    
    entity_history = (state["entity_history"] if configurable.should_write_history_entry_pass_previous_entries_sources
                     else state["entity_history_without_sources"])
    
    # Get relationship-specific prompt if available
    relationship_specific_prompt = ""
    if state.get("graph_settings"):
        raw_prompt = state.get("graph_settings", {}).get("relationship_specific_prompt")
        if raw_prompt:
            try:
                relationship_specific_prompt = raw_prompt.format(
                    entity=state.get("entity_name", "")
                )
            except:
                relationship_specific_prompt = raw_prompt
    
    review_result = await llm_reviewer.ainvoke([
        SystemMessage(content=configurable.should_write_history_entry_system_instructions.format(
            entity=state.get("entity_name"),
            current_date=state.get("current_date"),
            entity_history=entity_history,
            sources=state.get("sources"),
            last_hours=configurable.last_hours,
            relationship_specific_prompt=relationship_specific_prompt
        )),
        HumanMessage(content="Please review if we should write history entries.")
    ])
    
    if not review_result.entity_history_plans:
        return [
            Send("update_entity_history", {
                "entity_history_entries": [],
                "no_new_information": True
            })
        ]
    
    return [
        Send("assemble_history_entry", {
            "entity_history_plans": [plan],
            "entity_history": state.get("entity_history"),
            "sources": state.get("sources"),
            "entity_name": state.get("entity_name"),
            "entity_history_without_sources": state.get("entity_history_without_sources")
        })
        for plan in review_result.entity_history_plans
    ]


async def assemble_history_entry(state: EntityTrackerState, config: RunnableConfig):
    """Assemble a history entry from a plan."""
    entity_history_plan = state.get("entity_history_plans")[0] if state.get("entity_history_plans") else None
    
    if not entity_history_plan:
        return {"entity_history_entries": []}
    
    # Filter sources based on plan's source_numbers
    filtered_sources = []
    if entity_history_plan.source_numbers:
        all_sources = state.get("sources", [])
        for source in all_sources:
            if (source.metadata and 
                "source_number" in source.metadata and 
                source.metadata["source_number"] in entity_history_plan.source_numbers):
                filtered_sources.append(source)
    else:
        filtered_sources = state.get("sources", [])
    
    entity_history_entry = EntityHistoryEntry(
        content=entity_history_plan.event,
        sources=filtered_sources
    )
    
    return {"entity_history_entries": [entity_history_entry]}


async def should_update_entity_history(state: EntityTrackerState, config: RunnableConfig) -> Command[Literal["update_entity_history"]]:
    """Determine which entries should be added to entity history."""
    if state.get("no_new_information"):
        return Command(
            update={},
            goto="update_entity_history"
        )
    
    configurable = Configuration.from_runnable_config(config)
    
    llm_configs = create_llm_configs(configurable)
    llm_reviewer = await create_llm_from_config(llm_configs["llm_reviewer"], ShouldUpdateEntityHistory)
    
    # Format entries with numbers
    entity_history_entries = [
        f"Entry #{i+1}: {entry.content}"
        for i, entry in enumerate(state.get("entity_history_entries", []))
    ]
    
    entity_history_entry_numbers = [
        f"{i+1}"
        for i in range(len(state.get("entity_history_entries", [])))
    ]
    
    entity_history = (state["entity_history"] if configurable.should_update_entity_history_pass_previous_entries_sources
                     else state["entity_history_without_sources"])
    
    review_result = await llm_reviewer.ainvoke([
        SystemMessage(content=configurable.should_update_entity_history_system_instructions.format(
            entity=state.get("entity_name"),
            current_date=state.get("current_date"),
            entity_history=entity_history,
            entity_history_entries=entity_history_entries,
            entity_history_entry_numbers=entity_history_entry_numbers,
            last_hours=configurable.last_hours
        )),
        HumanMessage(content="Please review which entries to update.")
    ])
    
    if not review_result.entity_history_entries:
        return Command(
            update={},
            goto="update_entity_history"
        )
    
    # Filter entries based on review
    entity_history_entries_filtered = [
        state.get("entity_history_entries", [])[i-1]
        for i in review_result.entity_history_entries
    ]
    
    return Command(
        update={
            "entity_history_entries_filtered": entity_history_entries_filtered,
            "entity_id": state.get("entity_id")
        },
        goto="update_entity_history"
    )


async def update_entity_history(state: EntityTrackerState, config: RunnableConfig):
    """Update the entity history in the database."""
    if state.get("no_new_information") or not state.get("entity_history_entries_filtered"):
        return {
            "entity_history_output": EntityHistory(entries=[]),
            "no_new_information": True
        }
    
    # Save each entry to database
    history_entries = []
    for entry in state.get("entity_history_entries_filtered", []):
        save_entity_history_entry(
            entity_id=state.get("entity_id"),
            content=entry.content,
            sources=entry.sources,
            timestamp=state.get("current_date"),
            relationship_id=state.get("entity_relationship_id")
        )
        history_entries.append(entry)
    
    entity_history_output = EntityHistory(entries=history_entries)
    
    return {
        "entity_history_output": entity_history_output,
        "sources": [],
        "entity_id": state.get("entity_id"),
        "no_new_information": False
    }


# Build the graph
entity_builder = StateGraph(
    EntityTrackerState,
    input=EntityTrackerInput,
    output=EntityTrackerOutput,
    config_schema=Configuration
)

# Create retry policy for resilience
retry_policy = RetryPolicy(
    initial_interval=10,
    backoff_factor=3.0,
    max_interval=120,
    max_attempts=4,
    jitter=True
)

# Add nodes with retry policies
entity_builder.add_node("initialize_search", initialize_search)
entity_builder.add_node("create_universal_queries", create_universal_queries, retry=retry_policy)

entity_builder.add_node("search_web", search_web, retry=retry_policy)
entity_builder.add_node("review_web_sources", review_web_sources, retry=retry_policy)

entity_builder.add_node("search_email", search_email, retry=retry_policy)
entity_builder.add_node("review_email_sources", review_email_sources, retry=retry_policy)

entity_builder.add_node("search_youtube", search_youtube, retry=retry_policy)
entity_builder.add_node("review_youtube_sources", review_youtube_sources, retry=retry_policy)

entity_builder.add_node("search_speeches", search_speeches, retry=retry_policy)
entity_builder.add_node("review_speeches_sources", review_speeches_sources, retry=retry_policy)

entity_builder.add_node("search_scraper", search_scraper, retry=retry_policy)
entity_builder.add_node("review_scraper_sources", review_scraper_sources, retry=retry_policy)

entity_builder.add_node("gather_sources", gather_sources, retry=retry_policy)
entity_builder.add_node("assemble_history_entry", assemble_history_entry, retry=retry_policy)
entity_builder.add_node("should_update_entity_history", should_update_entity_history, retry=retry_policy)
entity_builder.add_node("update_entity_history", update_entity_history, retry=retry_policy)

# Add edges
entity_builder.add_edge(START, "initialize_search")
entity_builder.add_edge("initialize_search", "create_universal_queries")

# Parallel search branches
entity_builder.add_edge("create_universal_queries", "search_web")
entity_builder.add_edge("search_web", "review_web_sources")
entity_builder.add_edge("review_web_sources", "gather_sources")

entity_builder.add_edge("create_universal_queries", "search_email")
entity_builder.add_edge("search_email", "review_email_sources")
entity_builder.add_edge("review_email_sources", "gather_sources")

entity_builder.add_edge("create_universal_queries", "search_youtube")
entity_builder.add_edge("search_youtube", "review_youtube_sources")
entity_builder.add_edge("review_youtube_sources", "gather_sources")

entity_builder.add_edge("create_universal_queries", "search_speeches")
entity_builder.add_edge("search_speeches", "review_speeches_sources")
entity_builder.add_edge("review_speeches_sources", "gather_sources")

entity_builder.add_edge("create_universal_queries", "search_scraper")
entity_builder.add_edge("search_scraper", "review_scraper_sources")
entity_builder.add_edge("review_scraper_sources", "gather_sources")

# History entry pipeline
entity_builder.add_conditional_edges("gather_sources", should_write_history_entry, {
    "assemble_history_entry": "assemble_history_entry",
    "update_entity_history": "update_entity_history"
})
entity_builder.add_edge("assemble_history_entry", "should_update_entity_history")
entity_builder.add_edge("update_entity_history", END)

# Compile the graph
graph = entity_builder.compile()
graph.name = "Entity Tracker"

