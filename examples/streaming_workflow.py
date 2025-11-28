"""
Example of streaming the entity tracking workflow.

This demonstrates how to stream intermediate results as the graph executes.
"""

import asyncio
from entity_tracker import graph


async def main():
    """Stream the entity tracking process."""
    print("Streaming entity tracker execution...\n")
    
    input_data = {
        "entity_name": "Apple Inc",
        "entity_type": "organization",
        "current_date": "2024-01-15"
    }
    
    # Stream the workflow
    async for chunk in graph.astream(input_data):
        node_name = list(chunk.keys())[0] if chunk else "unknown"
        print(f"✓ Completed node: {node_name}")
        
        # Print interesting intermediate results
        if node_name == "initialize_search":
            data = chunk[node_name]
            print(f"  Entity: {data.get('entity_name')}")
            history = data.get("entity_history")
            if history:
                print(f"  Existing history entries: {len(history.entries)}")
        
        elif node_name == "create_universal_queries":
            queries = chunk[node_name].get("queries", [])
            if queries:
                print(f"  Generated queries: {len(queries)}")
                for q in queries[:3]:  # Show first 3
                    print(f"    - {q}")
        
        elif node_name == "gather_sources":
            sources = chunk[node_name].get("sources", [])
            print(f"  Total sources found: {len(sources)}")
        
        elif node_name == "update_entity_history":
            output = chunk[node_name].get("entity_history_output")
            if output:
                print(f"  New entries added: {len(output.entries)}")
    
    print("\n✓ Entity tracking complete!")


if __name__ == "__main__":
    asyncio.run(main())

