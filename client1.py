import asyncio
from datetime import datetime
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
import json

load_dotenv()

SERVERS = {
    'LedgerFlow': {
        "transport": "streamable_http",
        "url": "https://ledger-flow-mcp-339446203512.asia-south1.run.app/mcp"
    }
}


async def run_agent_turn(llm_with_tools, named_tools, messages):
    """Run one full agent turn — handles chained tool calls automatically."""
    while True:
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)

        # If no tool calls, we have the final text response
        if not getattr(response, 'tool_calls', None):
            return response.content, messages

        # Execute all tool calls in this turn
        for tc in response.tool_calls:
            tool_name = tc["name"]
            tool_args = tc.get("args") or {}
            tool_call_id = tc["id"]

            print(f"  → Calling tool: {tool_name}({tool_args})")

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


async def main():
    print("Connecting to MCP servers...")

    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()

    named_tools = {tool.name: tool for tool in tools}
    print(f"Loaded tools: {list(named_tools.keys())}")
    print("-" * 50)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    today = datetime.now().strftime("%d-%m-%Y")
    system_prompt = f"""Today's date is {today}.
You are a helpful general purpose assistant. You have access to a set of tools via MCP servers:
- An expense tracker to add expenses, list transactions, and summarize spending by category, all the transactions here are done in INR currency.
- Arithmetic operations for basic math calculations

Use these tools whenever the user's request relates to them. For everything else, answer naturally from your own knowledge like a general purpose assistant."""

    messages = [SystemMessage(content=system_prompt)]

    print("Assistant ready! Type 'quit' or 'exit' to stop.\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        messages.append(HumanMessage(content=user_input))

        try:
            reply, messages = await run_agent_turn(llm_with_tools, named_tools, messages)
            print(f"Assistant: {reply}\n")
        except Exception as e:
            print(f"Error: {e}\n")
            messages.pop()

if __name__ == '__main__':
    asyncio.run(main())