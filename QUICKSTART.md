# Quick Start Guide

This guide will get you up and running with Entity Tracker in under 5 minutes.

## Prerequisites

- Python 3.11 or higher
- OpenAI API key

## Installation

1. **Clone and setup**:
```bash
git clone https://github.com/yourusername/entity-tracker-langgraph.git
cd entity-tracker-langgraph
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure API keys**:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Your First Entity Track

Create a file `my_first_track.py`:

```python
import asyncio
from entity_tracker import graph

async def main():
    result = await graph.ainvoke({
        "entity_name": "Microsoft",
        "entity_type": "organization",
        "current_date": "2024-01-15"
    })
    
    if not result.get("no_new_information"):
        for entry in result["entity_history_output"].entries:
            print(f"• {entry.content}")
    else:
        print("No new developments found.")

asyncio.run(main())
```

Run it:
```bash
python my_first_track.py
```

## What Just Happened?

The Entity Tracker just:
1. ✅ Initialized search for "Microsoft"
2. ✅ Generated intelligent search queries
3. ✅ Searched the web for recent content
4. ✅ Reviewed and filtered sources using LLM
5. ✅ Created timeline entries for factual developments
6. ✅ Saved results to the in-memory database

## Next Steps

- **Customize search**: See `examples/custom_configuration.py`
- **Track relationships**: See `examples/relationship_tracking.py`
- **Stream results**: See `examples/streaming_workflow.py`
- **Run tests**: `pytest tests/`

## Common Issues

**No results found?**
- Check your OPENAI_API_KEY is set correctly
- Try increasing the time window: `last_hours=48` in configuration
- Enable debug mode: `Configuration(debug=True)`

**API errors?**
- Verify API keys in `.env`
- Check API rate limits
- Review error messages in debug mode

## Learn More

- **Full Documentation**: See `README.md`
- **Architecture**: See workflow diagram below
- **Examples**: Browse `examples/` directory

## Workflow Diagram

```
┌─────────────────────┐
│  Initialize Search  │
└──────────┬──────────┘
           │
    ┌──────▼───────┐
    │ Create Queries│
    └──────┬───────┘
           │
     ┌─────┴──────┐
     │   Search   │
     │  Multiple  │
     │  Sources   │
     └─────┬──────┘
           │
     ┌─────▼──────┐
     │   Review   │
     │  Sources   │
     └─────┬──────┘
           │
    ┌──────▼───────┐
    │Gather Sources│
    └──────┬───────┘
           │
    ┌──────▼───────────┐
    │ Create Timeline  │
    │    Entries       │
    └──────┬───────────┘
           │
    ┌──────▼───────────┐
    │  Save to DB      │
    └──────────────────┘
```

---

**Happy tracking! 🎯**

