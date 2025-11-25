"""Streaming utilities for chat responses."""
import json
from typing import AsyncGenerator


def get_friendly_tool_message(tool_name: str, tool_args: dict, stage: str = "start") -> str:
    """Generate user-friendly messages for tool invocations."""
    opp_name = tool_args.get('oppurtunity_name', tool_args.get('opportunity_name', 'Unknown'))
    opp_id = tool_args.get('opp_id', tool_args.get('id', 'Unknown'))
    stage_filter = tool_args.get('stage', None)
    
    tool_messages = {
        "create_opportunity": {
            "start": f"✨ Creating new opportunity: **{opp_name}**...",
            "complete": f"✅ Successfully created opportunity: **{opp_name}**!"
        },
        "list_opportunities": {
            "start": f"📋 Fetching opportunities{f' with stage **{stage_filter}**' if stage_filter else ''}...",
            "complete": "✅ Successfully retrieved all opportunities!"
        },
        "get_opportunity": {
            "start": f"🔍 Looking up opportunity #{opp_id}...",
            "complete": f"✅ Successfully found opportunity #{opp_id}!"
        },
        "update_opportunity": {
            "start": f"📝 Updating opportunity #{opp_id}...",
            "complete": f"✅ Successfully updated opportunity #{opp_id}!"
        },
        "delete_opportunity": {
            "start": f"🗑️ Deleting opportunity #{opp_id}...",
            "complete": f"✅ Successfully deleted opportunity #{opp_id}!"
        },
    }
    
    for key, messages in tool_messages.items():
        if key.lower() in tool_name.lower():
            return messages.get(stage, f"⚙️ Executing {tool_name}...")
    
    return f"⚙️ Executing {tool_name}..." if stage == "start" else f"✅ Completed {tool_name}!"


async def format_sse_event(data: dict) -> str:
    """Format data as Server-Sent Event."""
    return f"data: {json.dumps(data)}\n\n"
