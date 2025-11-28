"""
Example of tracking an entity with relationship context.

This demonstrates how to track entities in the context of their relationships
with other entities (e.g., "inflation in United States").
"""

import asyncio
from entity_tracker import graph


async def main():
    """Track inflation in the context of United States."""
    print("Tracking inflation → United States relationship...")
    
    result = await graph.ainvoke({
        "entity_name": "inflation",
        "entity_type": "concept",
        "related_entity_name": "United States",
        "related_entity_type": "location",
        "relationship_type": "affects",
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
            print(f"   Number of sources: {len(entry.sources)}")
            
            # Print source URLs
            for j, source in enumerate(entry.sources[:3], 1):  # First 3 sources
                if source.metadata and "url" in source.metadata:
                    print(f"   [{j}] {source.metadata['url']}")


if __name__ == "__main__":
    asyncio.run(main())

