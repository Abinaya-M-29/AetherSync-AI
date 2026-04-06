import os
import pickle
import sqlite3
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import json
from mcp.server.fastmcp import FastMCP
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google_auth_oauthlib.flow import Flow
from datetime import datetime, timedelta

#log to a file
logging.basicConfig(filename="google_tools.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
import json, os

QUEUE_FILE = "/tmp/email_queue.json"

# ===== CONFIG =====
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/blogger",
]

TOKEN_FILE = "token.pkl"


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

import httplib2

http = httplib2.Http(timeout=20)

creds = get_credentials()
gmail    = build("gmail",    "v1", credentials=creds)
calendar = build("calendar", "v3", credentials=creds)
tasks    = build("tasks",    "v1", credentials=creds)
blogger  = build("blogger",  "v3", credentials=creds, cache_discovery=False)


# def get_services():
#     creds = get_credentials()

#     gmail    = build("gmail",    "v1", credentials=creds)
#     calendar = build("calendar", "v3", credentials=creds)
#     tasks    = build("tasks",    "v1", credentials=creds)
#     blogger  = build("blogger",  "v3", credentials=creds)

#     return gmail, calendar, tasks, blogger
# ===== MCP SERVER =====
# mcp = FastMCP("google-tools")
mcp = FastMCP("AetherMCPServer", host="0.0.0.0", port=8080)


DB_PATH = "database/inventory.db"
logging.basicConfig(level=logging.INFO)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # rows behave like dicts
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@mcp.tool()
def query_db(sql: str, params: list = []) -> str:
    """
    Execute a SELECT query and return results as JSON.

    Args:
        sql:    A SELECT statement. No DDL or DML allowed here.
        params: Optional list of positional parameters (? placeholders).

    Example:
        sql    = "SELECT * FROM products WHERE stock_qty < ?"
        params = [10]
    """
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return json.dumps({"error": "Only SELECT statements are allowed in query_db."})

    try:
        conn = get_conn()
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        result = [dict(r) for r in rows]
        logging.info(f"query_db: {len(result)} rows — {sql[:80]}")
        logging.info(result)
        return json.dumps(result, default=str)
    except Exception as e:
        logging.error(f"query_db error: {e}")
        logging.info(result)
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_low_stock() -> str:
    """
    Return all products where stock_qty <= reorder_level.
    No SQL needed — use this for quick reorder alerts.
    """
    sql = """
        SELECT p.sku, p.name, p.stock_qty, p.reorder_level,
               c.name AS category, s.name AS supplier
        FROM   products p
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN suppliers  s ON s.id = p.supplier_id
        WHERE  p.stock_qty <= p.reorder_level
        ORDER  BY p.stock_qty ASC
    """
    conn = get_conn()
    rows = [dict(r) for r in conn.execute(sql).fetchall()]
    conn.close()
    logging.info(f"get_low_stock: found {json.dumps(rows, default=str)} low stock product(s)")
    return json.dumps(rows, default=str)

@mcp.tool()
def get_stock_and_offers(product_name: str) -> str:
    """
    input is product name or partial name, output is stock and offer information for matching products.
    Return stock and offer information for a specific product.
    """
    sql = """
        SELECT p.sku, p.name, p.stock_qty, p.reorder_level, p.unit_price, p.current_offer, p.offer_expires_at,
               c.name AS category, s.name AS supplier
        FROM   products p
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN suppliers  s ON s.id = p.supplier_id
        WHERE  p.name LIKE ?
    """
    logging.info(f"get_stock_and_offers: product_name={product_name} SQL={sql}")
    conn = get_conn()
    rows = [dict(r) for r in conn.execute(sql, (f"%{product_name}%",)).fetchall()]
    logging.info(f"get_stock_and_offers: found {json.dumps(rows, default=str)} matching product(s)")
    conn.close()
    return json.dumps(rows, default=str)

@mcp.tool()
def insert_feedback(payload: dict) -> str:
    """
    Insert feedback into the feedback_store table in the database.
    (source, sender_id, sender_name, subject, message, rating, sentiment) are parameters in the payload dict.
    """
    sql = """
        INSERT INTO feedback_store (source, sender_id, sender_name, subject, message, rating, sentiment)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    logging.info(f"insert_feedback: payload={payload} SQL={sql}")
    conn = get_conn()
    cur = conn.execute(sql, (
        payload.get("source"),
        payload.get("sender_id"),
        payload.get("sender_name"),
        payload.get("subject"),
        payload.get("message"),
        payload.get("rating"),
        payload.get("sentiment")
    ))
    conn.commit()
    conn.close()
    logging.info(f"insert_feedback: inserted feedback with id={cur.lastrowid}")
    return json.dumps({"rowcount": cur.rowcount, "lastrowid": cur.lastrowid})




@mcp.tool()
def execute_db(sql: str, params: list = []) -> str:
    """
    Execute an INSERT, UPDATE, or DELETE statement.

    Args:
        sql:    The DML statement to run.
        params: Optional positional parameters (? placeholders).

    Returns JSON with rowcount and last inserted id (if applicable).

    Example — restock a product:
        sql    = "UPDATE products SET stock_qty = stock_qty + ?, updated_at = CURRENT_TIMESTAMP WHERE sku = ?"
        params = [50, "EL-001"]
    """
    sql_upper = sql.strip().upper()
    forbidden = ("DROP", "TRUNCATE", "ALTER", "CREATE", "ATTACH", "DETACH", "PRAGMA")
    if any(sql_upper.startswith(kw) for kw in forbidden):
        return json.dumps({"error": f"Forbidden operation: {sql_upper.split()[0]}"})

    try:
        conn = get_conn()
        cur = conn.execute(sql, params)
        conn.commit()
        result = {"rowcount": cur.rowcount, "lastrowid": cur.lastrowid}
        conn.close()
        logging.info(f"execute_db: {result} — {sql[:80]}")
        return json.dumps(result)
    except Exception as e:
        logging.error(f"execute_db error: {e}")
        conn.rollback()
        conn.close()
        return json.dumps({"error": str(e)})



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

def get_blog_id(blogger, blog_url: str = None):
    """
    Resolve a Blog ID. If blog_url is provided, look it up by URL;
    otherwise return the first blog owned by the authenticated user.
    """
    if blog_url:
        blog = blogger.blogs().getByUrl(url=blog_url).execute()
        return blog["id"]
    blogs = blogger.blogs().listByUser(userId="self").execute()
    logging.info(f"get_blog_id: found {len(blogs.get('items', []))} blog(s)")
    if not blogs.get("items"):
        raise ValueError("No blogs found for this account.")
    return blogs["items"][0]["id"]

# ===== TOOL: SEND EMAIL =====
@mcp.tool()
def send_email(to: str, subject: str, body: str, html: bool = False):
    """
    Send an email via Gmail.

    Args:
        to:      Recipient email address (or comma-separated list).
        subject: Email subject line.
        body:    Email body — plain text, or HTML markup when html=True.
        schedule: Set True to schedule the email for later delivery.
        html:    Set True to send as HTML email; defaults to plain text.
    """
    logging.info(f"send_email: to={to} subject={subject}")
    # gmail, _, _, _ = get_services()

    if html:
        msg = MIMEMultipart("alternative")
        msg["To"]      = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))
    else:
        msg = MIMEText(body, "plain")
        msg["To"]      = to
        msg["Subject"] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    sent = gmail.users().messages().send(userId="me", body={"raw": raw}).execute()

    logging.info(f"send_email: message id={sent['id']}")
    return {"id": sent["id"], "status": "sent"}


@mcp.tool()
def create_meeting(
    summary: str,
    start: str,
    end: str,
    attendee_emails: list[str],
    description: str = "",
):
    """
    Create a Google Calendar event with a Google Meet link and send email invites.

    Args:
        summary:         Title of the meeting.
        start:           Start datetime in ISO 8601 format, e.g. 2026-04-05T10:00:00
        end:             End datetime in ISO 8601 format,   e.g. 2026-04-05T11:00:00
        attendee_emails: List of attendee email addresses.
        description:     Optional agenda/description for the meeting.
    """
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
        "end":   {"dateTime": end,   "timeZone": "Asia/Kolkata"},
        "attendees": [{"email": email} for email in attendee_emails],
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{summary[:8]}-{start[:10]}",  # unique per request
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email",  "minutes": 60},
                {"method": "popup",  "minutes": 10},
            ],
        },
        "guestsCanModifyEvent": False,
        "sendUpdates": "all",   # Google sends invite emails automatically
    }

    created = calendar.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1,   # required to generate Meet link
        sendUpdates="all",         # sends invite emails to all attendees
    ).execute()

    meet_link = (
        created.get("conferenceData", {})
               .get("entryPoints", [{}])[0]
               .get("uri", "No Meet link generated")
    )

    logging.info(f"create_meeting: id={created['id']} meet={meet_link}")
    return {
        "event_id":   created["id"],
        "event_link": created.get("htmlLink"),
        "meet_link":  meet_link,
        "attendees":  attendee_emails,
    }


# ===== TOOL: READ EMAILS =====
@mcp.tool()
def get_recent_emails(n: int):
    """Fetch last n Gmail messages."""
    logging.info("get_recent_emails: called")
    # gmail, _, _, _ = get_services()
    if n < 1 or n > 10:
        n = 5  # default to 5 to reduce risk of large responses; adjust as needed
    logging.info(f"get_recent_emails: fetching last {n} emails")

    results = gmail.users().messages().list(userId="me",labelIds=['INBOX'], maxResults=n).execute()
    messages = results.get("messages", [])[::-1]

    full_emails = []
    for msg in messages:
        msg_data = gmail.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        headers  = msg_data["payload"]["headers"]

        full_emails.append({
            "id":      msg["id"],
            "subject": next((h["value"] for h in headers if h["name"] == "Subject"), ""),
            "from":    next((h["value"] for h in headers if h["name"] == "From"),    ""),
            "body":    extract_body(msg_data["payload"]),
        })

    for each in full_emails:
        logging.info(f"Email ID: {each['id']} Subject: {each['subject']} From: {each['from']} Body Preview: {each['body']}")
    # logging.info(f"get_recent_emails: returned {full_email0s} email(s)")
    return full_emails


# ===== TOOL: CREATE CALENDAR EVENT =====
@mcp.tool()
def create_event(summary: str, start: str, end: str):
    """
    Create a Google Calendar event.

    Args:
        summary: Title of the event.
        start:   Start datetime in ISO 8601 format, e.g. 2026-04-05T10:00:00
        end:     End datetime in ISO 8601 format,   e.g. 2026-04-05T11:00:00
    """
    # _, calendar, _, _ = get_services()

    event = {
        "summary": summary,
        "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
        "end":   {"dateTime": end,   "timeZone": "Asia/Kolkata"},
    }

    created = calendar.events().insert(calendarId="primary", body=event).execute()
    logging.info(f"create_event: created event id={created['id']}")
    return created

# ===== TOOL: GET CALENDAR EVENTS FOR A DATE =====
@mcp.tool()
def get_events_for_date(date: str):
    """
    Fetch all Google Calendar events for a specific date.

    Args:
        date: Date in YYYY-MM-DD format, e.g. 2026-04-05
    """
    logging.info(f"get_events_for_date: date={date}")
    # _, calendar, _, _ = get_services()

    time_min = f"{date}T00:00:00+05:30"
    time_max = f"{date}T23:59:59+05:30"

    result = calendar.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = result.get("items", [])
    logging.info(f"get_events_for_date: found {len(events)} event(s)")

    return [
        {
            "id":       e.get("id"),
            "summary":  e.get("summary", "(No title)"),
            "start":    e.get("start", {}).get("dateTime") or e.get("start", {}).get("date"),
            "end":      e.get("end",   {}).get("dateTime") or e.get("end",   {}).get("date"),
            "location": e.get("location", ""),
            "description": e.get("description", ""),
        }
        for e in events
    ]


# ===== TOOL: GET TASKS =====
@mcp.tool()
def get_tasks(tasklist_name: str = None, include_completed: bool = False):
    """
    Retrieve tasks from a Google Tasks list.

    Args:
        tasklist_name:     Name of the task list to read (case-insensitive).
                           Defaults to the first/primary list if omitted.
        include_completed: Include completed tasks in the results (default False).
    """
    logging.info(f"get_tasks: tasklist_name={tasklist_name} include_completed={include_completed}")
    # _, _, tasks, _ = get_services()

    tasklists   = tasks.tasklists().list().execute()
    all_lists   = tasklists.get("items", [])

    if not all_lists:
        return {"error": "No task lists found."}

    if tasklist_name:
        matched = next((l for l in all_lists if l["title"].lower() == tasklist_name.lower()), None)
        tasklist_id = matched["id"] if matched else all_lists[0]["id"]
    else:
        tasklist_id = all_lists[0]["id"]

    show_hidden = "true" if include_completed else "false"

    result = tasks.tasks().list(
        tasklist=tasklist_id,
        showCompleted=show_hidden,
        showHidden=show_hidden,
    ).execute()

    items = result.get("items", [])
    logging.info(f"get_tasks: found {len(items)} task(s)")

    return [
        {
            "id":       t.get("id"),
            "title":    t.get("title", ""),
            "status":   t.get("status", ""),
            "due":      t.get("due", ""),
            "notes":    t.get("notes", ""),
            "updated":  t.get("updated", ""),
        }
        for t in items
    ]

# ===== TOOL: ADD TASK =====
@mcp.tool()
def add_task(title: str):
    """Add a task to the primary Google Tasks list."""
    # _, _, tasks, _ = get_services()

    tasklists   = tasks.tasklists().list().execute()
    tasklist_id = tasklists["items"][0]["id"]

    result = tasks.tasks().insert(tasklist=tasklist_id, body={"title": title}).execute()
    logging.info(f"add_task: created task id={result['id']}")
    return result

# ===== TOOL: ADD BLOGGER POST =====
@mcp.tool()
def add_blog_post(title: str, content: str, labels: list[str] = None, blog_url: str = None):
    """
    Publish a new post to a Blogger blog.

    Args:
        title:    Title of the blog post.
        content:  HTML content of the post body.
        labels:   Optional list of label/tag strings.
        blog_url: URL of the target blog (e.g. https://myblog.blogspot.com).
                  Omit to use the first blog on the account.
    """
    logging.info(f"add_blog_post: title={title}")
    # _, _, _, blogger = get_services()

    blog_id = get_blog_id(blogger, blog_url)

    post_body = {"title": title, "content": content}
    if labels:
        post_body["labels"] = labels

    post = blogger.posts().insert(blogId=blog_id, body=post_body).execute()
    logging.info(f"add_blog_post: post id={post['id']}")
    return {"id": post["id"], "url": post.get("url"), "published": post.get("published")}


# ===== TOOL: GET BLOGGER POSTS IN DATE RANGE =====
@mcp.tool()
def get_blog_posts(start_time: str, end_time: str, blog_url: str = None, max_results: int = 10):
    """
    Retrieve blog posts published within a date/time range.

    Args:
        start_time:  ISO 8601 start datetime, e.g. 2026-01-01T00:00:00+05:30
        end_time:    ISO 8601 end datetime,   e.g. 2026-04-05T23:59:59+05:30
        blog_url:    URL of the target blog. Omit to use the first blog on the account.
        max_results: Maximum number of posts to return (default 10).
    """
    logging.info(f"get_blog_posts: start={start_time} end={end_time}")
    # _, _, _, blogger = get_services()

    blog_id = get_blog_id(blogger, blog_url)

    result = blogger.posts().list(
        blogId=blog_id,
        startDate=start_time,
        endDate=end_time,
        maxResults=max_results,
        orderBy="PUBLISHED",
        fetchBodies=True,
    ).execute()

    posts = result.get("items", [])
    logging.info(f"get_blog_posts: found {len(posts)} post(s)")

    return [
        {
            "id":        p.get("id"),
            "title":     p.get("title"),
            "published": p.get("published"),
            "updated":   p.get("updated"),
            "url":       p.get("url"),
            "labels":    p.get("labels", []),
            "content":   p.get("content", "")[:500] + ("..." if len(p.get("content","")) > 500 else ""),
        }
        for p in posts
    ]


def _queue_email(to, subject, body):
    queue = _load_queue()
    queue.append({"to": to, "subject": subject, "body": body, "queued_at": datetime.now().isoformat()})
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f)

def _load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE) as f:
        return json.load(f)

def _clear_queue():
    if os.path.exists(QUEUE_FILE):
        os.remove(QUEUE_FILE)


@mcp.tool()
def add_to_queue(payload: dict):
    """Provide email info, calendar event details, or blog post content to be queued for later processing."""
    """
    {
        email: {
            "to": SUPPLIER_EMAIL,
            "subject": "Low Stock Alert: <product_name> (SKU: <sku>) — only <stock_qty> units left",
            "body": "Please prepare to restock <product_name> (SKU: <sku>). Current stock is critically low at <stock_qty> units. We will place the order during non-carbon hours to minimize environmental impact."
        },
        calendar_event: {
            "title": "Restock Review: <product_name>",
            "datetime": "2026-04-05T09:00:00",
            "duration_minutes": 30,
            "description": "Review restock plan for <product_name>. Current stock is critically low at <stock_qty> units."
        },
        blog_post: {
            "title": "Low Stock Alert: <product_name>",
            "content": "Only <stock_qty> units of <product_name> (SKU: <sku>) remaining. We will place the reorder during non-carbon hours to minimize environmental impact."
        }
    }
    """
    os.makedirs("tmp/schedule_queue", exist_ok=True)
    with open(f"tmp/schedule_queue/{datetime.now().isoformat()}.json", "w") as f:
        json.dump(payload, f, indent=2)
    # _queue_email(to, subject, body)
    logging.info(f"Item queued: {payload}")
    return {"status": "queued successfully"}

@mcp.tool()
def flush_queue() -> dict:
    """
    Send all queued items. Call this during non-carbon hours to drain the queue.
    Returns how many items were sent.
    """
    list_of_files = os.listdir("tmp/schedule_queue") if os.path.exists("tmp/schedule_queue") else []
    sent = 0
    for filename in sorted(list_of_files):
        with open(f"tmp/schedule_queue/{filename}") as f:
            payload = json.load(f)
            if "email" in payload:
                email = payload["email"]
                send_email(email["to"], email["subject"], email["body"])
                sent += 1
            if "calendar_meeting" in payload:
                event = payload["calendar_meeting"]
                create_meeting(
                    summary=event["summary"],
                    start=event["start"],
                    end=event["end"],
                    attendee_emails=event.get("attendee_emails", []),
                    description=event.get("description", "")
                )
                sent += 1
            if "blog_post" in payload:
                post = payload["blog_post"]
                add_blog_post(
                    title=post["title"],
                    content=post["content"]
                )
                sent += 1
        # os.remove(f"tmp/schedule_queue/{filename}")
    logging.info(f"flush_queue: sent {sent} item(s)")
    return {"status": "done", "sent": sent}

# @mcp.tool()
# def add_task(title: str):
#     """Add a Google Task"""
#     _, _, tasks = get_services()

#     tasklists = tasks.tasklists().list().execute()
#     tasklist_id = tasklists["items"][0]["id"]

#     task = {
#         "title": title
#     }

#     result = tasks.tasks().insert(
#         tasklist=tasklist_id,
#         body=task
#     ).execute()

#     return result


# ===== RUN SERVER =====
if __name__ == "__main__":

    mcp.run(transport="streamable-http")
    
    # mcp.run()
    # mcp.run(transport="sse", host="127.0.0.1", port=8005)