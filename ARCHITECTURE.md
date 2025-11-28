# Entity Tracker - Architecture & Workflow

This document provides a visual overview of the Entity Tracker's architecture and workflow.

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      Entity Tracker System                        │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User Input    │────▶│  LangGraph       │────▶│    Database     │
│                 │     │  Agent           │     │                 │
│ • Entity Name   │     │                  │     │ • Entity        │
│ • Entity Type   │     │ 13+ Nodes        │     │   History       │
│ • Relationships │     │ Parallel Search  │     │ • Sources       │
│ • Date          │     │ LLM Review       │     │ • Relationships │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               │
                        ┌──────▼──────┐
                        │   Search    │
                        │   Sources   │
                        └─────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │          │         │         │          │
    ┌─────▼────┐ ┌──▼───┐ ┌──▼────┐ ┌──▼──────┐ ┌─▼──────┐
    │   Web    │ │Email │ │YouTube│ │Speeches │ │Scraper │
    │  Search  │ │Search│ │Search │ │ Search  │ │ Search │
    └──────────┘ └──────┘ └───────┘ └─────────┘ └────────┘
```

## Detailed Workflow

### Phase 1: Initialization

```
┌──────────────────────┐
│  User provides:      │
│  - entity_name       │
│  - entity_type       │
│  - current_date      │
│  - (optional) config │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│  initialize_search            │
│                               │
│  • Validate inputs            │
│  • Construct entity context   │
│  • Retrieve existing history  │
│  • Set up relationships       │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  create_universal_queries     │
│                               │
│  • Generate base queries      │
│  • Add custom queries         │
│  • LLM generates complementary queries │
│  • Avoid duplicating existing queries  │
└──────────┬───────────────────┘
           │
           ▼
```

### Phase 2: Parallel Multi-Source Search

```
                    ┌──────────────────┐
                    │ Search Queries   │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │           │       │       │           │
    ┌────▼────┐ ┌───▼──┐ ┌──▼───┐ ┌─▼──────┐ ┌─▼──────┐
    │  Web    │ │Email │ │YouTube│ │Speeches │ │Scraper│
    │ Search  │ │Search│ │Search │ │ Search  │ │Search │
    └────┬────┘ └───┬──┘ └──┬───┘ └─┬──────┘ └─┬──────┘
         │          │       │       │           │
    ┌────▼────┐ ┌───▼──┐ ┌──▼───┐ ┌─▼──────┐ ┌─▼──────┐
    │ Review  │ │Review│ │Review │ │ Review  │ │Review │
    │ Sources │ │ Srcs │ │Sources│ │ Sources │ │ Srcs  │
    └────┬────┘ └───┬──┘ └──┬───┘ └─┬──────┘ └─┬──────┘
         │          │       │       │           │
         └──────────┴───────┴───────┴───────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │Gather Sources│
                    └──────┬───────┘
                           │
                           ▼
```

### Phase 3: Source Review & Filtering

```
┌─────────────────────────────────────────────┐
│  LLM-Driven Source Review                   │
│                                              │
│  For each source, check:                    │
│  ┌────────────────────────────────────────┐ │
│  │ 1. Development Significance             │ │
│  │    • Actual events vs. predictions      │ │
│  │    • Factual developments only          │ │
│  ├────────────────────────────────────────┤ │
│  │ 2. Temporal Validation                  │ │
│  │    • Event date within time window      │ │
│  │    • Distinguish from publication date  │ │
│  ├────────────────────────────────────────┤ │
│  │ 3. Relevance Check                      │ │
│  │    • Directly about entity              │ │
│  │    • Not already in history             │ │
│  ├────────────────────────────────────────┤ │
│  │ 4. Deduplication                        │ │
│  │    • Group similar sources              │ │
│  │    • Keep best primary source           │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Result: Filtered, high-quality sources     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
```

### Phase 4: Timeline Entry Creation

```
┌────────────────────────────────────────────┐
│  should_write_history_entry                 │
│                                             │
│  LLM analyzes sources and decides:         │
│  • Are there new factual developments?     │
│  • What events should be recorded?         │
│  • Which sources support each event?       │
│                                             │
│  Creates EntityHistoryPlan for each event  │
└──────────────┬─────────────────────────────┘
               │
               ▼
   ┌───────────────────────┐
   │  For each plan:       │
   │                       │
   │  assemble_history_    │
   │  entry                │
   │                       │
   │  • Extract event text │
   │  • Link sources       │
   │  • Format entry       │
   └───────────┬───────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  should_update_entity_history             │
│                                           │
│  Final quality check:                    │
│  • Semantic deduplication                │
│  • Materiality assessment                │
│  • Timeline coherence                    │
│                                           │
│  Filters entries to keep                 │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  update_entity_history                    │
│                                           │
│  • Save approved entries to database     │
│  • Link sources to entries               │
│  • Update entity timeline                │
│                                           │
│  Return: EntityHistory with new entries  │
└──────────────────────────────────────────┘
```

## Data Flow Diagram

```
Input                Process              Output
─────                ───────              ──────

Entity         ─▶   Initialize      ─▶   Entity Context
+ Type              Search               + History
+ Date                                   + Settings
                         │
                         ▼
                    Generate        ─▶   Search Queries
                    Queries
                         │
                         ▼
Queries        ─▶   Multi-Source    ─▶   Raw Sources
                    Search               (Web, Email, etc.)
                         │
                         ▼
Sources        ─▶   LLM Review      ─▶   Filtered Sources
+ History           & Filter             (High-quality)
                         │
                         ▼
Filtered       ─▶   Create Timeline ─▶   History Plans
Sources             Plans                (Events + Sources)
                         │
                         ▼
Plans          ─▶   Assemble        ─▶   Draft Entries
                    Entries              (Content + Sources)
                         │
                         ▼
Draft          ─▶   Final Review    ─▶   Approved Entries
Entries             & Filter             (Deduplicated)
                         │
                         ▼
Approved       ─▶   Save to         ─▶   Updated Entity
Entries             Database             History
```

## Node Execution Order

```
1.  START
2.  initialize_search
3.  create_universal_queries
    │
    ├─ 4a. search_web ────────▶ 5a. review_web_sources ─────┐
    ├─ 4b. search_email ──────▶ 5b. review_email_sources ───┤
    ├─ 4c. search_youtube ────▶ 5c. review_youtube_sources ─┼─▶ 6. gather_sources
    ├─ 4d. search_speeches ───▶ 5d. review_speeches_sources ┤
    └─ 4e. search_scraper ────▶ 5e. review_scraper_sources ─┘
                                                              │
                                                              ▼
                                               7. should_write_history_entry
                                                              │
                                      ┌───────────────────────┴─────────┐
                                      │                                 │
                                      ▼                                 ▼
                          8. assemble_history_entry          No new information
                          (parallel, one per plan)
                                      │
                                      ▼
                          9. should_update_entity_history
                                      │
                                      ▼
                          10. update_entity_history
                                      │
                                      ▼
                                    END
```

## State Management

```
┌─────────────────────────────────────────────────────────┐
│  EntityTrackerState (flows through all nodes)          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Input Fields:                                          │
│  • entity_name, entity_id, entity_type                  │
│  • related_entity_name, related_entity_type             │
│  • relationship_type, entity_relationship_id            │
│  • graph_settings, current_date                         │
│                                                         │
│  Working Fields:                                        │
│  • queries: list[str]                                   │
│  • web_sources, email_sources, youtube_sources, etc.    │
│  • sources: list[Document]                              │
│  • entity_history, entity_history_without_sources       │
│  • entity_history_plans, entity_history_entries         │
│                                                         │
│  Output Fields:                                         │
│  • entity_history_output: EntityHistory                 │
│  • no_new_information: bool                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Quality Control Layers

```
Layer 1: Query Generation
┌───────────────────────────────┐
│ • Complementary strategy      │
│ • No duplicates               │
│ • 5-word maximum              │
│ • No temporal references      │
└───────────┬───────────────────┘
            │
Layer 2: Source Review
┌───────────▼───────────────────┐
│ • Factual development filter  │
│ • Temporal validation         │
│ • Primary source preference   │
│ • Deduplication               │
└───────────┬───────────────────┘
            │
Layer 3: Entry Writing
┌───────────▼───────────────────┐
│ • 25-word maximum             │
│ • Active voice                │
│ • No speculation              │
│ • Attribution accuracy        │
└───────────┬───────────────────┘
            │
Layer 4: Timeline Curation
┌───────────▼───────────────────┐
│ • Semantic deduplication      │
│ • Materiality assessment      │
│ • Timeline coherence          │
│ • Final quality check         │
└───────────────────────────────┘
```

## Technology Stack

```
┌──────────────────────────────────────────────┐
│              Application Layer                │
│  • Entity Tracker Agent                      │
│  • Custom Prompts & Schemas                  │
│  • Business Logic                            │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│              Framework Layer                  │
│  • LangGraph (Workflow)                      │
│  • LangChain (LLM Integration)               │
│  • Pydantic (Data Validation)                │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│              Services Layer                   │
│  • OpenAI API (LLMs)                         │
│  • Tavily API (Web Search)                   │
│  • Custom Search Tools                       │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│              Storage Layer                    │
│  • In-Memory DB (Demo)                       │
│  • PostgreSQL (Production)                   │
│  • Vector Stores (Future)                    │
└──────────────────────────────────────────────┘
```

---

*For more details, see README.md and the code documentation.*

