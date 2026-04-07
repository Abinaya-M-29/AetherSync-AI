from backend.api.app import app
# from backend.workflow.graph_flow import app_graph
# import asyncio
# print(app_graph.invoke({
#     "input": "Hello, how are you?"
# }))

# from backend.workflows.graph_router import run as run_orchestrator

# async def test_orchestrator():
#     result = await run_orchestrator("Check emails for any customer feedback and store it in the database")

#     print(result)

# asyncio.run(test_orchestrator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)