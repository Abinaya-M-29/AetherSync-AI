import os
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
import pickle
import sqlite3
from typing import Dict, Any
import httpx
from contextlib import asynccontextmanager
# from mcp_server.google_tools import get_flow
from fastapi.middleware.cors import CORSMiddleware
from google_auth_oauthlib.flow import Flow
# from backend.workflow.graph_flow import app_graph
# from backend.workflow.graph_flow import app_graph_async
from backend.workflows.graph_router import run as run_orchestrator
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

load_dotenv("secrets/.env", override=True)

MCP_URL = "http://localhost:8080/mcp"


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

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    domain:   str
    response: str
    error:    str = ""

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


@app.post("/flush-queue")
async def flush_queue():
    result = await run_orchestrator("Flush the MCP schedule queue and return the result.")
    print(result)
    return {"status": "accepted", "message": "Done flush operation."}

@app.post("/check-inventory")
async def check_inventory_low():
    result = await run_orchestrator("Check our database and send emails if any inventory  low")
    return {"status": "completed", "result": result}

@app.post("/automated_quotation_agent")
async def automated_quotation_agent():
    result = await run_orchestrator("Call automated Sales Quotation Agent. check email and generate quotation")
    return {"status": "completed", "result": result}

@app.post("/automated_feedback_agent")
async def automated_feedback_agent():
    result = await run_orchestrator("Check emails for any customer feedback and store it in the database")
    return {"status": "completed", "result": result}

@app.post("/chat_async")
async def chat_async(req: dict):
    try:
        # user_input = req["message"]

        # result = await app_graph_async.ainvoke({
        #     "input": user_input
        # })
        # print("Result:", result)
        # return {
        #     "response": result["output"]
        # }
        result = await run_orchestrator(req.message)
 
        return ChatResponse(
            domain=result.get("domain", "unknown"),
            response=result.get("response", ""),
            error=result.get("error", ""),
        )
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


# ── Inventory Endpoints ──────────────────────────────────────────────

def get_db_connection():
    conn = sqlite3.connect("database/inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/inventory/products")
def get_inventory():
    conn = get_db_connection()
    try:
        products = conn.execute("""
            SELECT 
                p.id, 
                p.sku, 
                p.name as itemName, 
                c.name as category_name, 
                p.stock_qty as stock, 
                p.reorder_level
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
        """).fetchall()

        result = []
        for p in products:
            status = 'Medium'
            if p['stock'] <= p['reorder_level']:
                status = 'Low'
            elif p['stock'] > p['reorder_level'] * 1.5:
                status = 'High'
                
            if p['stock'] == 0:
                status = 'Out of Stock'

            result.append({
                "id": p["id"],
                "sku": p["sku"],
                "itemName": p["itemName"],
                "location": p["category_name"] or "Main Warehouse", # using category as location proxy
                "stock": p["stock"],
                "status": status,
                "reorder_level": p["reorder_level"]
            })
        return result
    finally:
        conn.close()

@app.post("/api/inventory/products/{sku}/sell")
def sell_inventory(sku: str, payload: Dict[str, Any], background_tasks: BackgroundTasks):
    quantity = int(payload.get("quantity", 1))
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check current stock
        product = cursor.execute("SELECT id, stock_qty, reorder_level FROM products WHERE sku = ?", (sku,)).fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        current_stock = product['stock_qty']
        reorder_level = product['reorder_level']
        
        if current_stock < quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {current_stock}")
            
        new_stock = current_stock - quantity
        
        # Update stock
        cursor.execute("UPDATE products SET stock_qty = ? WHERE sku = ?", (new_stock, sku))
        
        # Log stock movement
        cursor.execute(
            "INSERT INTO stock_movements (product_id, movement, qty, note) VALUES (?, ?, ?, ?)",
            (product['id'], 'OUT', quantity, f"Sold {quantity} units via UI")
        )
        
        conn.commit()
        
        # Trigger automation if stock crosses reorder threshold
        if current_stock > reorder_level and new_stock <= reorder_level:
            trigger_prompt = (
                f"inventory check: stock for SKU {sku} has dropped to {new_stock} units "
                f"which is at or below the reorder level of {reorder_level}. "
                f"Please check all low stock products in the inventory database and send reorder emails to suppliers."
            )
            background_tasks.add_task(run_orchestrator, trigger_prompt)
            
        return {"success": True, "new_stock": new_stock, "message": f"Successfully sold {quantity} units"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# ── Activity Log Endpoints ──────────────────────────────────────────────────

@app.get("/api/activity/logs")
def get_activity_logs(limit: int = 20, domain: str = None):
    conn = get_db_connection()
    try:
        if domain:
            rows = conn.execute(
                """
                SELECT * FROM agent_runs
                WHERE domain = ?
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (domain, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM agent_runs
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/api/activity/logs/{run_id}")
def get_activity_log_detail(run_id: str):
    conn = get_db_connection()
    try:
        run = conn.execute(
            "SELECT * FROM agent_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        steps = conn.execute(
            """
            SELECT * FROM agent_steps
            WHERE run_id = ?
            ORDER BY step_order ASC
            """,
            (run_id,),
        ).fetchall()

        result = dict(run)
        result["steps"] = [dict(s) for s in steps]
        return result
    finally:
        conn.close()