import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from mcp_config import SERVERS, get_system_prompt, run_agent_turn, setup_client

load_dotenv()


async def main():
    print("Connecting to MCP servers...")

    tools, named_tools = await setup_client()

    print(f"Loaded tools: {list(named_tools.keys())}")
    print("-" * 50)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    messages = [SystemMessage(content=get_system_prompt())]

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
            # Print tool calls to terminal
            async def on_tool_call(tool_name, tool_args):
                print(f"  → Calling tool: {tool_name}({tool_args})")

            reply, messages = await run_agent_turn(
                llm_with_tools, named_tools, messages,
                on_tool_call=on_tool_call
            )
            print(f"Assistant: {reply}\n")
        except Exception as e:
            print(f"Error: {e}\n")
            messages.pop()


if __name__ == '__main__':
    asyncio.run(main())