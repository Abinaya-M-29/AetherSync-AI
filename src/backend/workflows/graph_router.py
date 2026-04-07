"""
LangGraph orchestrator.

Flow:
  user input
      │
      ▼
  classify_intent   ← lightweight Gemini call, returns one of 5 domain labels
      │
      ▼
  route_to_agent    ← conditional edge picks the right ADK subagent
      │
      ▼
  run_agent         ← calls the chosen subagent, streams result back
      │
      ▼
  END
"""

import asyncio
import os

import traceback
from typing import Literal, TypedDict

from langgraph.graph import StateGraph, END
from google import genai
from google.adk.runners import Runner
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from backend.adk_agent.adk_agent import (
    run_inventory_check,
    create_email_agent,
    create_calendar_agent,
    create_tasks_agent,
    create_blog_agent,
    create_flush_agent,
    check_email_generate_quotation_agent,
    check_feedback_and_write_to_db
)
from dotenv import load_dotenv
load_dotenv("secrets/.env", override=True)

from backend.db.run_logger import start_run, log_step, finish_run

# ── Gemini for the intent classifier (ultra-light call, no tools needed) ──
# genai.configure()  # uses GOOGLE_API_KEY from env
# _classifier_model = genai.GenerativeModel("gemini-2.0-flash")
MODEL_NAME = "gemini-2.5-flash-lite"
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 4. Use client.models.generate_content instead of GenerativeModel
# response = client.models.generate_content(
#     model='gemini-2.0-flash', 
#     contents='Hello'
# )

Domain = Literal["inventory", "email", "calendar", "tasks", "blog", "flush_queue", "unknown"]

_AGENT_FACTORIES = {
    "inventory": run_inventory_check,
    # "email":     create_email_agent,
    # "calendar":  create_calendar_agent,
    # "tasks":     create_tasks_agent,
    # "blog":      create_blog_agent,
    "flush_queue": create_flush_agent,
    "check_email_generate_quotation_agent": check_email_generate_quotation_agent,
    "check_feedback_and_write_to_db": check_feedback_and_write_to_db
}

# ── State ──────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    run_id:   str
    input:    str
    domain:   Domain
    response: str
    error:    str


# ── Nodes ──────────────────────────────────────────────────────────────────

async def classify_intent(state: AgentState) -> AgentState:
    """
    Ask Gemini to classify the user's query into one of the five domains.
    Returns a single lowercase label — no extra text.
    """
    prompt = f"""Classify the following user request into exactly one of these categories:
inventory, email, calendar, tasks, blog, flush_queue, check_email_generate_quotation_agent, check_feedback_and_write_to_db

Rules:
- inventory → anything about stock, products, SKUs, suppliers, reorder levels, database queries
- flush_queue → anything about flushing the MCP schedule queue
- check_email_generate_quotation_agent → anything about  RFQ's (Request for Quotation) or Sales Quotations, or the specific agent that handles these (check_email_generate_quotation_agent) 
- check_feedback_and_write_to_db → anything about checking customer feedback and writing to the database, or the specific agent that handles these (check_feedback_and_write_to_db)

Reply with ONLY the category word, nothing else.

User request: {state['input']}"""

    # response = await asyncio.to_thread(
    #     _classifier_model.generate_content, prompt
    # )
    response = client.models.generate_content(
        model=MODEL_NAME, 
        contents=prompt
    )
    domain_raw = response.text.strip().lower()
    domain: Domain = domain_raw if domain_raw in _AGENT_FACTORIES else "unknown"
    print(f"[router] classified as: {domain!r}")
    
    log_step(
        state["run_id"],
        1,
        "classify",
        f"Intent classified as '{domain}'"
    )
    
    return {**state, "domain": domain}


def route_decision(state: AgentState) -> str:
    """Conditional edge: return the domain label (or 'unknown')."""
    return state["domain"]


async def run_inventory(state: AgentState)  -> AgentState: return await _run(state, "inventory")
# async def run_email(state: AgentState)      -> AgentState: return await _run(state, "email")
# async def run_calendar(state: AgentState)   -> AgentState: return await _run(state, "calendar")
# async def run_tasks(state: AgentState)      -> AgentState: return await _run(state, "tasks")
# async def run_blog(state: AgentState)       -> AgentState: return await _run(state, "blog")
async def run_flush(state: AgentState)      -> AgentState: return await _run(state, "flush_queue")
async def run_check_email_generate_quotation(state: AgentState) -> AgentState: return await _run(state, "check_email_generate_quotation_agent")
async def run_check_feedback_and_write_to_db(state: AgentState) -> AgentState: return await _run(state, "check_feedback_and_write_to_db")

async def handle_unknown(state: AgentState) -> AgentState:
    return {
        **state,
        "response": (
            "I couldn't determine which domain your request belongs to. "
            "Try rephrasing — e.g. 'send an email to…', 'what's in stock for…', "
            "'schedule a meeting with…', 'add a task to…', or 'write a blog post about…'."
        ),
    }


async def _run(state: AgentState, domain: str) -> AgentState:
    """Instantiate the ADK agent for `domain` and run it against the user's input."""
    run_id = state.get("run_id")
    try:
        factory = _AGENT_FACTORIES[domain]
        # agent   = await factory()
        
        # Better error context on factory failure
        try:
            agent = await factory()
            if run_id: log_step(run_id, 2, "init", f"Agent factory '{domain}' initialized")
        except Exception as e:
            raise RuntimeError(f"MCP session init failed: {e}") from e

        # ADK agent.run() is synchronous in some versions — wrap just in case
        # if asyncio.iscoroutinefunction(agent.run):
        #     result = await agent.run(state["input"])
        # else:
        #     result = await asyncio.to_thread(agent.run, state["input"])

        # # ADK returns an object with a .text or .response attribute depending on version
        # response_text = (
        #     result.text
        #     if hasattr(result, "text")
        #     else str(result)
        # )
        # return {**state, "response": response_text}
        # ADK requires a Runner + SessionService to execute an LlmAgent
        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent,
            app_name=domain,
            session_service=session_service,
        )

        # Create a session
        session = await session_service.create_session(
            app_name=domain,
            user_id="user",
            session_id=f"{domain}_session" if not run_id else f"{domain}_session_{run_id}",
        )

        if run_id: log_step(run_id, 3, "init", "MCP toolset loaded and session started")

        user_message = genai.types.Content(
            role="user",
            parts=[genai.types.Part(text=state["input"])]
        )

        # Run the agent and collect the final response
        response_text = ""
        all_text_parts = []   # accumulate ALL text from any model turn
        tools_called = []
        step_counter = 4
        
        async for event in runner.run_async(
            user_id="user",
            session_id=f"{domain}_session" if not run_id else f"{domain}_session_{run_id}",
            new_message=user_message,
        ):
            # ── Capture ANY model text (not just final) ──────────────────
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    # Collect text from model turns
                    if hasattr(part, "text") and part.text and part.text.strip():
                        all_text_parts.append(part.text.strip())

                    # Log tool responses
                    if hasattr(part, "function_response") and part.function_response:
                        tool_name = part.function_response.name
                        if run_id:
                            log_step(run_id, step_counter, "tool_response", f"Tool returned: {tool_name}")
                        step_counter += 1

            # ── Log model function calls ──────────────────────────────────
            if hasattr(event, "model_response") and event.model_response and event.model_response.parts:
                for part in event.model_response.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        tool_name = part.function_call.name
                        tools_called.append(tool_name)
                        args_dict = None
                        if hasattr(part.function_call, "args"):
                            try:
                                args_dict = dict(part.function_call.args)
                            except Exception:
                                args_dict = str(part.function_call.args)

                        if run_id:
                            log_step(
                                run_id,
                                step_counter,
                                "tool_call",
                                f"Calling tool: {tool_name}",
                                payload_dict={"tool": tool_name, "args": args_dict}
                            )
                        step_counter += 1

                    # Also collect text from model_response parts
                    if hasattr(part, "text") and part.text and part.text.strip():
                        all_text_parts.append(part.text.strip())

        # ── Build response text ───────────────────────────────────────────
        if all_text_parts:
            response_text = all_text_parts[-1]   # use last meaningful text
        elif tools_called:
            response_text = f"Agent completed successfully. Tools used: {', '.join(tools_called)}."
        else:
            response_text = "Agent completed but returned no text response."

        if run_id:
            log_step(run_id, step_counter, "complete", "Agent execution finished")
            finish_run(run_id, response_text=response_text)

        return {**state, "response": response_text}


    except Exception as exc:
        traceback.print_exc()
        
        print(f"[router] error in {domain} agent: {exc}")
        if run_id:
            log_step(run_id, 999, "error", f"Error: {exc}")
            finish_run(run_id, error_str=str(exc), domain=domain)
            
        return {**state, "response": f"Error in {domain} agent: {exc}", "error": str(exc)}

async def test_email_mcp():
    factory = _AGENT_FACTORIES["email"]
    agent = await factory()
    print("✅ MCP session created successfully")

    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="email", session_service=session_service)
    await session_service.create_session(app_name="email", user_id="user", session_id="test")

    msg = genai.types.Content(role="user", parts=[genai.types.Part(text="list 1 recent emails")])
    async for event in runner.run_async(user_id="user", session_id="test", new_message=msg):
        print(f"Event: is_final={event.is_final_response()}, has_content={event.content is not None}")
        
        if event.is_final_response():
            # Guard: content can be None if the agent ends on a tool call turn
            if event.content and event.content.parts:
                # Find the first part that actually has text
                text_parts = [p.text for p in event.content.parts if hasattr(p, "text") and p.text]
                if text_parts:
                    print("✅ Response:", text_parts[0])
                else:
                    print("⚠️ Final response has no text parts:", event.content.parts)
            else:
                print("⚠️ Final response has no content — agent may have ended on a tool call")



# ── Graph assembly ─────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    # Nodes
    g.add_node("classify", classify_intent)
    g.add_node("inventory", run_inventory)
    # g.add_node("email",     run_email)
    # g.add_node("calendar",  run_calendar)
    # g.add_node("tasks",     run_tasks)
    # g.add_node("blog",      run_blog)
    g.add_node("flush_queue", run_flush)
    g.add_node("check_email_generate_quotation_agent", run_check_email_generate_quotation)
    g.add_node("check_feedback_and_write_to_db", run_check_feedback_and_write_to_db)
    g.add_node("unknown",   handle_unknown)

    # Entry
    g.set_entry_point("classify")

    # Conditional routing after classify
    g.add_conditional_edges(
        "classify",
        route_decision,
        {
            "inventory": "inventory",
            # "email":     "email",
            # "calendar":  "calendar",
            # "tasks":     "tasks",
            # "blog":      "blog",
            "flush_queue": "flush_queue",
            "check_email_generate_quotation_agent": "check_email_generate_quotation_agent",
            "check_feedback_and_write_to_db": "check_feedback_and_write_to_db",
            "unknown":   "unknown",
        },
    )

    nodes_list = ("inventory" , "flush_queue", "check_email_generate_quotation_agent", "check_feedback_and_write_to_db", "unknown")
    # All domain nodes go to END
    for node in nodes_list:
        g.add_edge(node, END)

    return g.compile()


# Compiled graph — import this in your app/API layer
orchestrator = build_graph()


# ── Convenience runner ─────────────────────────────────────────────────────

async def run(user_input: str) -> dict:
    """
    Entry point for the multi-agent system.

    Returns:
        {
            "input":    original query,
            "domain":   classified domain,
            "response": agent's answer,
            "error":    error string or ""
        }
    """
    run_id = start_run("unknown", "orchestrator", user_input)

    initial_state: AgentState = {
        "run_id":   run_id,
        "input":    user_input,
        "domain":   "unknown",
        "response": "",
        "error":    "",
    }
    final_state = await orchestrator.ainvoke(initial_state)

    # Update DB with the actual classified domain now that we have it
    finish_run(
        run_id,
        response_text=final_state.get("response", ""),
        error_str=final_state.get("error", ""),
        domain=final_state.get("domain", "unknown"),
    )

    return final_state