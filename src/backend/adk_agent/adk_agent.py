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
from datetime import datetime
load_dotenv("secrets/.env")

MCP_URL = "http://localhost:8080/mcp"

GEMINI_MODEL = "gemini-2.5-flash-lite"

model = Gemini(
    model_name=GEMINI_MODEL,  # or "gemini-1.5-pro"
)

CARBON_HOURS = {
    "non_carbon": [0, 1, 2, 3, 4, 5,  19, 23],
    "carbon": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,  20, 21, 22 ],
}


"""
inventory_agent:
1. Check inventory - "Check `products` table from database and send emails if any inventory low"
- Check `products` table  if its low in database 
- do following during non carbon hours only, only if its out of stock send during carbon hours
    - send a notification message in email to raw materials person 
    - send a meeting invite for restoring , 
    - post a blog that "only {n} left"
"""

SUPPLIER_EMAIL = "ajithdschrozahan@gmail.com"   # raw materials contact
YOUR_EMAIL     = "inocajith21.5@gmail.com"     # for CC / meeting organiser

def build_inventory_prompt() -> str:
    now        = datetime.now()
    hour       = now.hour
    is_carbon  = hour in CARBON_HOURS["carbon"]
    carbon_str = "CARBON hours (high grid carbon intensity)" if is_carbon else "NON-CARBON hours (low grid carbon intensity)"
    date_str   = now.strftime("%Y-%m-%d")
    time_str   = now.strftime("%H:%M")

    # Part 1: dynamic values — use f-string here
    header = (
        f"You are an inventory management agent. Current time: {time_str} on {date_str}.\n"
        f"Grid status right now: {carbon_str} (hour={hour}).\n"
        f"Supplier email: {SUPPLIER_EMAIL}\n"
    )

    # Part 2: instruction body — plain string, NO f-string
    # Use {product_name} freely here, ADK won't touch it because...
    # we'll join and pass as a non-f-string template
    body = """
## Step 1 — Check inventory
Query the `products` table via the database tool [get_low_stock]. For each product note:
- sku, name, stock_qty, reorder_level
- Flag LOW if stock_qty > 0 AND stock_qty < reorder_level  
- Flag OUT if stock_qty == 0

## Step 2 — Actions based on grid status

### NON-CARBON hours — act on LOW + OUT items:
For each flagged product:
1. Email SUPPLIER_EMAIL with subject:
   "Low Stock Alert: <product_name> (SKU: <sku>) — only <stock_qty> units left"
2. Calendar meeting titled "Restock Review: <product_name>" tomorrow 9 AM IST, 30 min.
3. Blog post: "Only <stock_qty> units of <product_name> remaining. Reorder in progress."

### CARBON hours — act on OUT items ONLY:
1. Email SUPPLIER_EMAIL: "URGENT — Out of Stock: <product_name> (SKU: <sku>)"
2. Calendar meeting: "URGENT Restock: <product_name>" tomorrow 9 AM IST, 30 min.
3. Blog post: "<product_name> is currently out of stock."

### CARBON hours — for LOW items
You MUST call the `add_to_queue` tool.

Call it with this exact structure:
{
    'email': {
        'to': SUPPLIER_EMAIL,
        'subject': 'Low Stock Alert: <product_name> (SKU: <sku>) — only <stock_qty> units left',
        'body': 'Please prepare to restock <product_name> (SKU: <sku>). Current stock is critically low at <stock_qty> units. We will place the order during non-carbon hours to minimize environmental impact.'
    },
    'calendar_meeting': {
        'summary': 'Restock Review: <product_name>',
        'start': '<tomorrow\'s date>T09:00:00',
        'end': '<tomorrow\'s date>T09:30:00',
        'attendee_emails': [SUPPLIER_EMAIL],
        'description': 'Review restock plan for <product_name>. Current stock is critically low at <stock_qty> units.'
    },
    'blog_post': {
        'title': 'Low Stock Alert: <product_name>',
        'content': 'Only <stock_qty> units of <product_name> (SKU: <sku>) remaining. We will place the reorder during non-carbon hours to minimize environmental impact.'
    }
}

## Step 3 — Summary
Return: products checked, how many LOW/OUT, actions taken, current grid status.
"""
    return header + body



async def run_inventory_check():
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=MCP_URL)
    )
    all_tools = await toolset.get_tools()
    
    # tools = await _load_tools(["create_meeting", "add_blog_post", "send_email", "get_low_stock", "add_to_queue"])
    agent = Agent(
        model=GEMINI_MODEL,
        tools=all_tools,
        instruction=build_inventory_prompt(),
        name="inventory_agent",
    )
    return agent

async def create_flush_agent():
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=MCP_URL)
    )
    all_tools = await toolset.get_tools()
    agent = Agent(
        model=GEMINI_MODEL,
        tools=all_tools,
        instruction="call the `flush_queue` tool with no arguments",
        name="flush_agent",
    )
    return agent

# async def check_email_generate_quotation_agent():
#     # toolset = McpToolset(
#     #     connection_params=StreamableHTTPConnectionParams(url=MCP_URL)
#     # )
#     tools = await _load_tools(["get_recent_emails", "get_stock_and_offers", "send_email"])
#     agent = Agent(
#         model=GEMINI_MODEL,
#         tools=tools,
#         name="email_quotation_rfq_agent",
#         instruction="""
# You are an automated Sales Quotation Agent for sending replies for RFQs. You have access to three specific tools: 

# RFQ:
# SENDER_EMAIL: ajithdschrozahan@gmail.com
# EMAIL_SUBJECT: Request for Quotation: Wireless Mouse
# EMAIL_BODY: Hello, we are interested in purchasing 50 units of your Wireless Mouse (SKU: EL-001). Please provide us with a quotation including your best price, available offers
# (if any), and estimated delivery time. Looking forward to your prompt response.



# 1. check the stock and offers of 'Wireless Mouse' product

# 2. Quotation & Response
# - Once you have the stock/offer data, draft a professional quotation.
# - Call `send_email(to=..., subject=..., body=...)` for each valid RFQ.

# ### STRICT OPERATIONAL RULES:
# - TOOL EXECUTION: You must call the tools. Do not just describe what you would do.
# - NO MANUAL INTERVENTION: Do not ask the user "Should I check stock?" or "Should I send the email?" Proceed automatically.
# - FINAL REPORT: Only after all `send_email` calls are finished, provide a short summary of your actions.
# """
#     )
#     return agent



async def check_email_generate_quotation_agent():
    # toolset = McpToolset(
    #     connection_params=StreamableHTTPConnectionParams(url=MCP_URL)
    # )
    tools = await _load_tools(["get_recent_emails", "get_stock_and_offers", "send_email"])
    agent = Agent(
        model=GEMINI_MODEL,
        tools=tools,
        name="email_quotation_rfq_agent",
        instruction="""
You are an automated Sales Quotation Agent for sending replies for RFQs. You have access to three specific tools: 
1. `get_recent_emails`
2. `get_stock_and_offers`
3. `send_email`

1. Fetch last 3 emails using `get_recent_emails` and check if any email contains a Request for Quotation (RFQ) for any products
listed here: ["Wireless Mouse", "Mechanical Keyboard", "USB-C Hub 7-in-1", "A4 Notebook (Pack 5)", "Ball Pen Box (50pcs)"]. An RFQ email will typically have a subject like "Request for Quotation" and may mention quantity and other details in the body.

2. check the stock and offers of product using `get_stock_and_offers` tool for each RFQ email found. Extract the product name from the email (e.g., "Wireless Mouse") and use it as the input to `get_stock_and_offers`.

3. Quotation & Response
- Once you have the stock/offer data, draft a professional quotation in text format. Include the product name, available stock, unit price, any current offers based on typical lead times.
- Call `send_email(to=..., subject=..., body=...)` for each valid RFQ.

### STRICT OPERATIONAL RULES:
- TOOL EXECUTION: You must call the tools. Do not just describe what you would do.
- FINAL REPORT: Only after all `send_email` calls are finished, provide a short summary of your actions.
"""
    )
    return agent


async def check_feedback_and_write_to_db():
    # toolset = McpToolset(
    #     connection_params=StreamableHTTPConnectionParams(url=MCP_URL)
    # )
    tools = await _load_tools(["get_recent_emails", "insert_feedback"])
    agent = Agent(
        model=GEMINI_MODEL,
        tools=tools,
        name="feedback_store_agent",
        instruction="""
You are an automated Feedback Store Agent for storing feedback from emails. You have access to two specific tools: 
1. `get_recent_emails`
2. `insert_feedback`

1. Fetch last 3 emails using `get_recent_emails` and check if any email contains customer feedback about products. Feedback emails may have subjects like "Feedback on [Product Name]" or "Complaint about [Product Name]". Extract the following details from each feedback email:
- sender's email (sender_id)
- sender's name (if available in the email body or signature)
- subject of the email
- main message content (the feedback itself)
- rating (if the email contains a rating, e.g., "I rate this product 4 out of 5")
- sentiment (determine if the feedback is positive, negative, or neutral based on the content)

2. For each feedback email found, call the `insert_feedback` tool with the extracted details to store it in the database.

### STRICT OPERATIONAL RULES:
- TOOL EXECUTION: You must call the tools. Do not just describe what you would do.
- FINAL REPORT: Only after all `send_email` calls are finished, provide a short summary of your actions.
"""
    )
    return agent


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

# async def create_inventory_agent() -> Agent:
#     tools = await _load_tools(["query_db", "execute_db", "get_low_stock"])
#     return Agent(
#         name="inventory_agent",
#         model=GEMINI_MODEL,
#         tools=tools,
#         instruction=(
#             "You manage a SQLite inventory database. "
#             "Use query_db for SELECT queries, execute_db for INSERT/UPDATE/DELETE, "
#             "and get_low_stock to surface reorder alerts. "
#             "Always confirm destructive changes before running execute_db. "
#             "Return results as concise summaries unless the user asks for raw data."
#             "After every tool call, you MUST respond with a natural language summary "
#             "of the result. Never end your turn silently after a tool call — "
#             "always follow up with a clear text reply to the user."
#         ),
#     )




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
    