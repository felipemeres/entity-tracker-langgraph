"""
Example of tracking with custom configuration.

This demonstrates how to override default configuration settings.
"""

import asyncio
from entity_tracker import graph
from entity_tracker.configuration import Configuration


async def main():
    """Track with custom configuration."""
    
    # Create custom configuration
    config = Configuration(
        # Use different models
        llm_query_creator="openai/gpt-4o-mini",
        llm_reviewer="openai/gpt-4o",
        llm_writer="openai/gpt-4o",
        
        # Search settings
        search_web_enabled=True,
        search_web_max_results=10,  # More results
        search_email_enabled=False,
        search_youtube_enabled=False,
        
        # Time windows
        last_hours=48,  # Look back 2 days instead of 1
        search_web_last_days=2,
        
        # Enable debug mode
        debug=True,
    )
    
    print("Tracking Tesla with custom configuration...")
    print(f"  - Web search: {config.search_web_max_results} results max")
    print(f"  - Time window: {config.last_hours} hours")
    print(f"  - Debug mode: {config.debug}\n")
    
    result = await graph.ainvoke(
        {
            "entity_name": "Tesla",
            "entity_type": "organization",
            "current_date": "2024-01-15"
        },
        config={"configurable": config.__dict__}
    )
    
    # Print results
    if result.get("no_new_information"):
        print("\nNo new developments found.")
    else:
        print(f"\nFound {len(result['entity_history_output'].entries)} new developments:")
        print("="*80)
        
        for i, entry in enumerate(result["entity_history_output"].entries, 1):
            print(f"\n{i}. {entry.content}")


if __name__ == "__main__":
    asyncio.run(main())

