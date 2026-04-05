## Fixed Agent Implementation

import asyncio
import os
import logging
import pdb

# import google.cloud.logging
# from asyncio import tools
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
import google.auth
import google.auth.transport.requests
import google.oauth2.id_token
from google.adk.agents.callback_context import CallbackContext
# from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
# from google.adk.types import UserMessage
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioServerParameters
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.models import Gemini
import os
from dotenv import load_dotenv
load_dotenv("secrets/.env")

# import nest_asyncio
# nest_asyncio.apply()  # allows nested event loops



# This assumes you have run 'gcloud auth application-default login'
model = Gemini(
    model_name="gemini-1.5-flash",  # or "gemini-1.5-pro"
)
# from google.adk.models.lite_llm import LiteLlm
# model = LiteLlm(model="ollama_chat/qwen2.5:7b")

async def create_agent_with_remote_mcp():
    # Note: Use the base URL. The MCP client handles the /sse and /messages paths.
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="http://localhost:8080/mcp", 
        )
    )

    # Await the tools from the remote MCP server
    tools = await toolset.get_tools()
    print(f"Loaded tools from MCP server: {[tool.name for tool in tools]}")

    agent = Agent(
        name="google_tools_agent",
        # Ensure 'model' is defined globally or passed in
        model=model,
        tools=tools,
        instruction="You are a helpful assistant with access to Gmail, Google Calendar, and Google Tasks."
    )
    return agent

# def run_agent(user_input):
async def run_agent_async(user_input):
    agent = await create_agent_with_remote_mcp()
    runner = InMemoryRunner(agent=agent, app_name="GoogleToolsApp")

    await runner.session_service.create_session(
        app_name="GoogleToolsApp",
        user_id="default_user",
        session_id="default_session",
    )

    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_input)]
    )

    # Use 'async for' if the runner returns an async generator
    events = runner.run(
        user_id="default_user",
        session_id="default_session",
        new_message=message
    )

    for event in events:
        if event.is_final_response():
            response_text = "".join(part.text for part in event.content.parts if hasattr(part, "text"))
            # print(f"Assistant: {response_text}")
    return {"response": response_text}
    
# if __name__ == "__main__":
#    run_agent("Give me the last 1 emails in my inbox")