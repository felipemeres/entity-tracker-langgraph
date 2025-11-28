"""
Basic example of tracking an entity.

This example demonstrates the simplest way to use the Entity Tracker.
"""

import asyncio
from entity_tracker import graph


async def main():
    """Track the Federal Reserve for recent developments."""
    print("Tracking Federal Reserve...")
    
    result = await graph.ainvoke({
        "entity_name": "Federal Reserve",
        "entity_type": "organization",
        "current_date": "2024-01-15"
    })
    
    # Print results
    if result.get("no_new_information"):
        print("\nNo new developments found.")
    else:
        print(f"\nFound {len(result['entity_history_output'].entries)} new developments:")
        print("="*80)
        
        for i, entry in enumerate(result["entity_history_output"].entries, 1):
            print(f"\n{i}. {entry.content}")
            print(f"   Sources: {len(entry.sources)}")
            
            # Print first source details
            if entry.sources:
                source = entry.sources[0]
                if source.metadata:
                    print(f"   URL: {source.metadata.get('url', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())

