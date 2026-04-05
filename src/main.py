from backend.api.app import app
# from backend.workflow.graph_flow import app_graph

# print(app_graph.invoke({
#     "input": "Hello, how are you?"
# }))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)