from datetime import datetime
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import ToolMessage
import json

# ─────────────────────────────────────────────
# SERVERS CONFIG
# ─────────────────────────────────────────────

SERVERS = {
    'LedgerFlow': {
        "transport": "streamable_http",
        "url": "https://ledger-flow-mcp-hz5uqwqwoq-el.a.run.app/mcp"
    }
}


# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────
def get_system_prompt(user_id: str) -> str:
    today = datetime.now().strftime("%d-%m-%Y")
    return f"""Today's date is {today}. The current user's ID is: {user_id}. Always pass this exact value as the user_id argument to every tool call without exception.
You are a helpful general purpose assistant. You have access to a set of tools via MCP servers:
- An expense tracker to add expenses, list transactions, and summarize spending by category. All transactions are in INR currency.
- Arithmetic operations for basic math calculations.
Use these tools whenever the user's request relates to them. For everything else, answer naturally from your own knowledge like a general purpose assistant."""


# ─────────────────────────────────────────────
# SHARED AGENT LOGIC
# ─────────────────────────────────────────────

async def run_agent_turn(llm_with_tools, named_tools, messages, on_tool_call=None):
    """Run one full agent turn — handles chained tool calls automatically.
    
    Args:
        llm_with_tools: LLM bound with tools
        named_tools: Dict of tool_name -> tool
        messages: Conversation history list
        on_tool_call: Optional async callback(tool_name, tool_args) called before each tool execution
                      Used by Chainlit to show tool call status in the UI
    """
    while True:
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)

        # No tool calls means we have the final text response
        if not getattr(response, 'tool_calls', None):
            return response.content, messages

        # Execute all tool calls in this turn
        for tc in response.tool_calls:
            tool_name = tc["name"]
            tool_args = tc.get("args") or {}
            tool_call_id = tc["id"]

            # Fire the optional callback (used by Chainlit for UI updates)
            if on_tool_call:
                await on_tool_call(tool_name, tool_args)

            if tool_name not in named_tools:
                result = {"error": f"Tool '{tool_name}' not found"}
            else:
                result = await named_tools[tool_name].ainvoke(tool_args)

            messages.append(
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=json.dumps(result)
                )
            )


async def setup_client():
    """Initialize MCP client, tools, and return named_tools dict."""
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    named_tools = {tool.name: tool for tool in tools}
    return tools, named_tools