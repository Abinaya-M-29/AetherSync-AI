# import asyncio
# from typing import TypedDict
# # import nest_asyncio
# # nest_asyncio.apply()
# from langgraph.graph import StateGraph
# from backend.adk_agent.adk_agent import run_agent_async
# class AgentState(TypedDict):
#     input: str
#     output: str
    

# async def agent_node(state: AgentState):
#     print("Agent received input:", state)
#     # result = asyncio.run(run_agent_async(state["input"]))
#     result = await run_agent_async(state["input"])
#     return {"output": result["response"]}

# graph = StateGraph(AgentState)
# graph.add_node("agent", agent_node)

# graph.set_entry_point("agent")
# graph.set_finish_point("agent")

# app_graph_async = graph.compile()


