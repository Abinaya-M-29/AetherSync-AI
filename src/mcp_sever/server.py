import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from mcp.server.fastmcp import FastMCP
import logging

#log to a file
logging.basicConfig(filename="google_tools.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ===== CONFIG =====
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]

TOKEN_FILE = "token.pkl"

from google_auth_oauthlib.flow import Flow

def get_flow():
    return Flow.from_client_secrets_file(
        "./secrets/credentials.json",
        scopes=SCOPES,
        redirect_uri="http://localhost:8005/oauth2callback"
    )

# ===== AUTH =====
def get_credentials():
    with open("./secrets/token.pkl", "rb") as f:
        return pickle.load(f)
    # creds = None

    # if os.path.exists(TOKEN_FILE):
    #     with open(TOKEN_FILE, "rb") as token:
    #         creds = pickle.load(token)

    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             "credentials.json", SCOPES
    #         )
    #         creds = flow.run_local_server(port=0)

    #     with open(TOKEN_FILE, "wb") as token:
    #         pickle.dump(creds, token)

    # return creds


def get_services():
    creds = get_credentials()

    gmail = build("gmail", "v1", credentials=creds)
    calendar = build("calendar", "v3", credentials=creds)
    tasks = build("tasks", "v1", credentials=creds)

    return gmail, calendar, tasks


# ===== MCP SERVER =====
# mcp = FastMCP("google-tools")
mcp = FastMCP("GoogleToolsServer", host="0.0.0.0", port=8080)


def extract_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8")

            # fallback to HTML if plain text not found
            if part["mimeType"] == "text/html":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8")

    else:
        data = payload["body"].get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8")

    return ""

# ===== TOOL: READ EMAILS =====
@mcp.tool()
def get_recent_emails():
    """Fetch last 1 Gmail messages"""
    logging.info(f"read  emails: called")
    gmail, _, _ = get_services()
    logging.info(f"read  emails: called")

    # results = gmail.users().messages().list(
    #     userId="me", maxResults=5
    # ).execute()
    # # print("Fetched emails:", results)
    # logging.info(f"Fetched emails: {results}")

    # return results.get("messages", [])
    results = gmail.users().messages().list(
        userId="me",
        maxResults=1
    ).execute()
    
    
    messages = results.get("messages", [])
    full_emails = []
    messages = messages[::-1]  # reverse to get oldest first

    for msg in messages:
        msg_data = gmail.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        headers = msg_data["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")

        body = extract_body(msg_data["payload"])

        full_emails.append({
            "id": msg["id"],
            "subject": subject,
            "from": sender,
            "body": body
        })
    logging.info(f"Fetched emails: {results}")

    return full_emails


# ===== TOOL: CREATE CALENDAR EVENT =====
@mcp.tool()
def create_event(summary: str, start: str, end: str):
    """
    Create calendar event
    start/end format: 2026-04-05T10:00:00
    """
    _, calendar, _ = get_services()

    event = {
        "summary": summary,
        "start": {
            "dateTime": start,
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end,
            "timeZone": "Asia/Kolkata"
        },
    }

    created_event = calendar.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return created_event


# ===== TOOL: ADD TASK =====
@mcp.tool()
def add_task(title: str):
    """Add a Google Task"""
    _, _, tasks = get_services()

    tasklists = tasks.tasklists().list().execute()
    tasklist_id = tasklists["items"][0]["id"]

    task = {
        "title": title
    }

    result = tasks.tasks().insert(
        tasklist=tasklist_id,
        body=task
    ).execute()

    return result


# ===== RUN SERVER =====
if __name__ == "__main__":

    mcp.run(transport="streamable-http")
    
    # mcp.run()
    # mcp.run(transport="sse", host="127.0.0.1", port=8005)