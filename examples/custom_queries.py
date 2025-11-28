"""
Example of tracking with custom search queries.

This demonstrates how to provide custom search queries through graph_settings.
"""

import asyncio
from entity_tracker import graph


async def main():
    """Track with predefined custom queries."""
    
    print("Tracking Amazon with custom search queries...\n")
    
    result = await graph.ainvoke({
        "entity_name": "Amazon",
        "entity_type": "organization",
        "current_date": "2024-01-15",
        "graph_settings": {
            # Custom search queries specific to Amazon
            "search_queries": [
                "Amazon AWS revenue",
                "Amazon Prime membership",
                "Amazon fulfillment centers",
                "Jeff Bezos Amazon",
                "Amazon antitrust"
            ],
            # Optional: custom prompt for this specific entity relationship
            "relationship_specific_prompt": (
                "Focus on business operations, revenue, and regulatory developments "
                "related to {entity}."
            )
        }
    })
    
    # Print results
    if result.get("no_new_information"):
        print("No new developments found.")
    else:
        print(f"Found {len(result['entity_history_output'].entries)} new developments:")
        print("="*80)
        
        for i, entry in enumerate(result["entity_history_output"].entries, 1):
            print(f"\n{i}. {entry.content}")
            
            # Show which sources were used
            if entry.sources:
                print(f"   Supported by {len(entry.sources)} source(s)")
                # Show unique domains
                domains = set()
                for source in entry.sources:
                    if source.metadata and "url" in source.metadata:
                        url = source.metadata["url"]
                        domain = url.split("//")[-1].split("/")[0]
                        domains.add(domain)
                if domains:
                    print(f"   Domains: {', '.join(sorted(domains))}")


if __name__ == "__main__":
    asyncio.run(main())

