import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import pickle
# from mcp_server.google_tools import get_flow
from fastapi.middleware.cors import CORSMiddleware
from google_auth_oauthlib.flow import Flow
# from backend.workflow.graph_flow import app_graph
from backend.workflow.graph_flow import app_graph_async

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/blogger",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_flow():
    return Flow.from_client_secrets_file(
        "secrets/credentials.json",
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/oauth2callback"
    )

flow = get_flow()


@app.get("/login")
def login():
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )
    return RedirectResponse(auth_url)


@app.get("/oauth2callback")
def oauth_callback(request: Request):
    flow.fetch_token(authorization_response=str(request.url))

    creds = flow.credentials

    with open("secrets/token.pkl", "wb") as f:
        pickle.dump(creds, f)

    return {"status": "authenticated"}


# @app.post("/chat")
# async def chat(req: dict):
#     user_input = req["message"]

#     result = app_graph.invoke({
#         "input": user_input
#     })
#     print("Result:", result)
#     return {
#         "response": result["output"]
#     }
    
    
@app.post("/chat_async")
async def chat_async(req: dict):
    try:
        user_input = req["message"]

        result = await app_graph_async.ainvoke({
            "input": user_input
        })
        print("Result:", result)
        return {
            "response": result["output"]
        }
    except Exception as e:
        print("Error during async chat:", str(e))
        return {
            "response": "An error occurred while processing your request."
        }
    
# def chat_with_memory(user_input, session_id):
#     history = load_chat(session_id)

#     result = app_graph.invoke({
#         "input": user_input,
#         "history": history
#     })

#     save_chat(session_id, user_input, result["output"])

#     return result["output"]