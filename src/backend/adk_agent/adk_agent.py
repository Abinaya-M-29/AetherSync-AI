"""
ADK subagents — one per domain.
Each agent is created async and receives only the MCP tools relevant to its domain.
"""

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.models import Gemini
import os
from dotenv import load_dotenv
load_dotenv("secrets/.env")

MCP_URL = "http://localhost:8080/mcp"

GEMINI_MODEL = "gemini-2.5-flash-lite"

model = Gemini(
    model_name=GEMINI_MODEL,  # or "gemini-1.5-pro"
)
# ---------------------------------------------------------------------------
# Helper: load a filtered subset of MCP tools
# ---------------------------------------------------------------------------

async def _load_tools(names: list[str]) -> list:
    """Fetch all tools from MCP and return only those whose names are in `names`."""
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=MCP_URL)
    )
    all_tools = await toolset.get_tools()
    filtered = [t for t in all_tools if t.name in names]
    print(f"[MCP] loaded {[t.name for t in filtered]}")
    return filtered


# ---------------------------------------------------------------------------
# Inventory agent
# ---------------------------------------------------------------------------

async def create_inventory_agent() -> Agent:
    tools = await _load_tools(["query_db", "execute_db", "get_low_stock"])
    return Agent(
        name="inventory_agent",
        model=GEMINI_MODEL,
        tools=tools,
        instruction=(
            "You manage a SQLite inventory database. "
            "Use query_db for SELECT queries, execute_db for INSERT/UPDATE/DELETE, "
            "and get_low_stock to surface reorder alerts. "
            "Always confirm destructive changes before running execute_db. "
            "Return results as concise summaries unless the user asks for raw data."
            "After every tool call, you MUST respond with a natural language summary "
            "of the result. Never end your turn silently after a tool call — "
            "always follow up with a clear text reply to the user."
        ),
    )


# ---------------------------------------------------------------------------
# Email agent
# ---------------------------------------------------------------------------

async def create_email_agent() -> Agent:
    tools = await _load_tools(["send_email", "get_recent_emails"])
    return Agent(
        name="email_agent",
        model=GEMINI_MODEL,
        tools=tools,
        instruction=(
            "You handle Gmail via the send_email and get_recent_emails tools. "
            "When sending, always confirm the recipient and subject with the user first "
            "unless they have already provided both. "
            "When reading emails, summarise clearly — sender, subject, key points."
            "After every tool call, you MUST respond with a natural language summary "
            "of the result. Never end your turn silently after a tool call — "
            "always follow up with a clear text reply to the user."
        ),
    )


# ---------------------------------------------------------------------------
# Calendar agent
# ---------------------------------------------------------------------------

async def create_calendar_agent() -> Agent:
    tools = await _load_tools(["create_event", "create_meeting", "get_events_for_date"])
    return Agent(
        name="calendar_agent",
        model=GEMINI_MODEL,
        tools=tools,
        instruction=(
            "You manage Google Calendar. "
            "Use create_meeting (with Google Meet link) for meetings with attendees. "
            "Use create_event for personal reminders or blocks with no attendees. "
            "Use get_events_for_date to check what's already scheduled. "
            "All datetimes are Asia/Kolkata (IST). "
            "Dates must be ISO 8601: 2026-04-05T10:00:00. "
            "Always confirm time and attendees before creating anything."
            "After every tool call, you MUST respond with a natural language summary "
            "of the result. Never end your turn silently after a tool call — "
            "always follow up with a clear text reply to the user."
        ),
    )


# ---------------------------------------------------------------------------
# Tasks agent
# ---------------------------------------------------------------------------

async def create_tasks_agent() -> Agent:
    tools = await _load_tools(["get_tasks", "add_task"])
    return Agent(
        name="tasks_agent",
        model=GEMINI_MODEL,
        tools=tools,
        instruction=(
            "You manage Google Tasks. "
            "Use get_tasks to list pending or completed tasks. "
            "Use add_task to create a new task in the primary list. "
            "Keep responses short and actionable."
            "After every tool call, you MUST respond with a natural language summary "
            "of the result. Never end your turn silently after a tool call — "
            "always follow up with a clear text reply to the user."
        ),
    )


# ---------------------------------------------------------------------------
# Blog agent
# ---------------------------------------------------------------------------

async def create_blog_agent() -> Agent:
    tools = await _load_tools(["add_blog_post", "get_blog_posts"])
    return Agent(
        name="blog_agent",
        model=GEMINI_MODEL,
        tools=tools,
        instruction=(
            "You manage a Blogger blog. "
            "Use add_blog_post to publish new posts — content must be valid HTML. "
            "Use get_blog_posts to retrieve posts in a date range. "
            "Ask for title and content before publishing if not provided. "
            "Confirm publish action with the user before calling add_blog_post."
            "After every tool call, you MUST respond with a natural language summary "
            "of the result. Never end your turn silently after a tool call — "
            "always follow up with a clear text reply to the user."
        ),
    )
    
# async def run_agent_async(user_input):
#     agent = await create_agent_with_remote_mcp()
#     runner = InMemoryRunner(agent=agent, app_name="GoogleToolsApp")

#     await runner.session_service.create_session(
#         app_name="GoogleToolsApp",
#         user_id="default_user",
#         session_id="default_session",
#     )

#     message = types.Content(
#         role="user",
#         parts=[types.Part.from_text(text=user_input)]
#     )

#     # Use 'async for' if the runner returns an async generator
#     events = runner.run(
#         user_id="default_user",
#         session_id="default_session",
#         new_message=message
#     )

#     for event in events:
#         if event.is_final_response():
#             response_text = "".join(part.text for part in event.content.parts if hasattr(part, "text"))
#             # print(f"Assistant: {response_text}")
#     return {"response": response_text}
    