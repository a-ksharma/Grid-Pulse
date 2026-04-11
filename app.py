import chainlit as cl
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from mcp_config import get_system_prompt, run_agent_turn, setup_client
from chainlit.server import app as fastapi_app
from fastapi.responses import JSONResponse
import os

load_dotenv()

@fastapi_app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})



# GOOGLE OAUTH

@cl.oauth_callback
def oauth_callback(provider_id: str, token: str, raw_user_data: dict, default_user: cl.User,) -> cl.User | None:
    """Called after Google OAuth login. Return user object or None to reject."""
    if provider_id == "google":
        return cl.User(
            identifier=raw_user_data.get("email"),
            metadata={
                "name": raw_user_data.get("name"),
                "avatar": raw_user_data.get("picture"),
                "provider": "google"
            }
        )
    return None


# CHAT START

@cl.on_chat_start
async def on_chat_start():
    # Get logged in user
    user = cl.user_session.get("user")
    user_id = user.identifier  # this is their Google email

    loading = cl.Message(content="Connecting to MCP servers, please wait...")
    await loading.send()

    try:
        tools, named_tools = await setup_client()

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        llm_with_tools = llm.bind_tools(tools)

        cl.user_session.set("llm_with_tools", llm_with_tools)
        cl.user_session.set("named_tools", named_tools)
        cl.user_session.set("user_id", user_id)
        cl.user_session.set("messages", [SystemMessage(content=get_system_prompt(user_id))])

        tool_names = list(named_tools.keys())
        name = user.metadata.get("name", user_id)

        loading.content = f"Welcome, {name}! Connected with tools: `{'`, `'.join(tool_names)}`\n\nHow can I help you today?"
        await loading.update()

    except Exception as e:
        loading.content = f"Failed to connect to MCP servers: {str(e)}"
        await loading.update()


# ON MESSAGE

@cl.on_message
async def on_message(message: cl.Message):
    llm_with_tools = cl.user_session.get("llm_with_tools")
    named_tools = cl.user_session.get("named_tools")
    messages = cl.user_session.get("messages")

    if not llm_with_tools or not named_tools:
        await cl.Message(content="Session not initialized. Please refresh the page.").send()
        return

    messages.append(HumanMessage(content=message.content))

    thinking_msg = cl.Message(content="")
    await thinking_msg.send()
    

    try:
        async def on_tool_call(tool_name, tool_args):
            async with cl.Step(name=f"Tool: {tool_name}") as step:
                step.input = tool_args
                await step.update()

        reply, messages = await run_agent_turn(
            llm_with_tools,
            named_tools,
            messages,
            on_tool_call=on_tool_call
        )

        thinking_msg.content = reply if isinstance(reply, str) else str(reply)
        await thinking_msg.update()

        cl.user_session.set("messages", messages)

    except Exception as e:
        thinking_msg.content = f"Sorry, something went wrong: {str(e)}"
        await thinking_msg.update()
        messages.pop()
        cl.user_session.set("messages", messages)
