import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import pickle
import sqlite3
from typing import Dict, Any
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
def sell_inventory(sku: str, payload: Dict[str, Any]):
    quantity = int(payload.get("quantity", 1))
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check current stock
        product = cursor.execute("SELECT id, stock_qty FROM products WHERE sku = ?", (sku,)).fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        current_stock = product['stock_qty']
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
        return {"success": True, "new_stock": new_stock, "message": f"Successfully sold {quantity} units"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()