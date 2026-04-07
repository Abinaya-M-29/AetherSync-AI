import sqlite3
import os
DB_PATH = "database/inventory.db"

def seed():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── Tables ──────────────────────────────────────────────
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT NOT NULL UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS suppliers (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        email      TEXT,
        phone      TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS products (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        sku           TEXT NOT NULL UNIQUE,
        name          TEXT NOT NULL,
        category_id   INTEGER REFERENCES categories(id),
        supplier_id   INTEGER REFERENCES suppliers(id),
        unit_price    REAL NOT NULL DEFAULT 0.0,
        stock_qty     INTEGER NOT NULL DEFAULT 0,
        reorder_level INTEGER NOT NULL DEFAULT 10,
        current_offer TEXT,
        offer_expires_at DATETIME,
        created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS stock_movements (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id  INTEGER REFERENCES products(id),
        movement    TEXT CHECK(movement IN ('IN','OUT','ADJUST')) NOT NULL,
        qty         INTEGER NOT NULL,
        note        TEXT,
        moved_at    DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS feedback_store (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,              -- 'email', 'web', 'mobile', 'chatbot'
        sender_id TEXT,                    -- email, user_id, phone, etc.
        sender_name TEXT,
        subject TEXT,
        message TEXT NOT NULL,
        rating INTEGER,
        sentiment TEXT,
        received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        processed BOOLEAN DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS agent_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT UNIQUE NOT NULL,
        agent_name TEXT,
        domain TEXT,
        input TEXT,
        status TEXT CHECK(status IN ('running', 'completed', 'failed')),
        response TEXT,
        error TEXT,
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        finished_at DATETIME
    );

    CREATE TABLE IF NOT EXISTS agent_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT REFERENCES agent_runs(run_id),
        step_order INTEGER,
        step_type TEXT,
        description TEXT,
        payload TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ── Seed data ────────────────────────────────────────────
    cur.executemany("INSERT OR IGNORE INTO categories(name) VALUES(?)", [
        ("Electronics",), ("Stationery",), ("Furniture",), ("Apparel",),
    ])

    cur.executemany(
        "INSERT OR IGNORE INTO suppliers(name, email, phone) VALUES(?,?,?)", [
        ("TechSource Pvt Ltd",  "orders@techsource.in",  "+91-9000000001"),
        ("OfficeMart",          "supply@officemart.in",  "+91-9000000002"),
        ("FurniCo",             "sales@furnico.in",      "+91-9000000003"),
    ])

    cur.executemany("""
        INSERT OR IGNORE INTO products
            (sku, name, category_id, supplier_id, unit_price, stock_qty, reorder_level, current_offer, offer_expires_at)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, [
        ("EL-001", "Wireless Mouse",        1, 1, 499.00,  45, 10, "20% off",  "2024-12-31"),
        ("EL-002", "Mechanical Keyboard",   1, 1, 1899.00, 4, 5, "5% off", "2024-12-31"),
        ("EL-003", "USB-C Hub 7-in-1",      1, 1, 1299.00, 12, 8, "15% off",  "2024-12-31"),
        ("ST-001", "A4 Notebook (Pack 5)",  2, 2, 149.00,  80, 20, "5% off",  "2024-12-31"),
        ("ST-002", "Ball Pen Box (50pcs)",  2, 2,  99.00,  60, 15, "10% off", "2024-12-31"),
        ("FU-001", "Ergonomic Chair",       3, 3, 8999.00,  0,  2, "25% off",  "2024-12-31"),
        ("FU-002", "Standing Desk",         3, 3,15999.00,  4,  2, "10% off",  "2024-12-31"),
        ("AP-001", "Company T-Shirt (M)",   4, 2, 399.00,  30, 5, "Buy 2 Get 1 Free", "2024-12-31"),
    ])

    cur.executemany("""
        INSERT INTO stock_movements (product_id, movement, qty, note)
        VALUES (?,?,?,?)
    """, [
        (1, "IN",  100, "Initial stock"),
        (1, "OUT",  55, "Sold to client A"),
        (2, "IN",   30, "Initial stock"),
        (2, "OUT",  10, "Internal use"),
        (6, "IN",   10, "Initial stock"),
        (6, "OUT",   2, "Office setup"),
    ])
    
    cur.executemany("""
        INSERT INTO feedback_store (source, sender_id, sender_name, subject, message, rating, sentiment)
        VALUES (?,?,?,?,?,?,?)
    """, [
        ("email", "customer1@example.com", "John Doe", "Feedback on Wireless Mouse", "I love the new Wireless Mouse!", 5, "positive"),
        ("email", "customer2@example.com", "Jane Smith", "Complaint about Mechanical Keyboard", "The keyboard is not responsive enough.", 2, "negative"),
        ("web", "user123", "Alice Johnson", "Suggestion for Standing Desk", "It would be great if the desk had built-in cable management.", 4, "neutral"),
    ])

    conn.commit()
    conn.close()
    print("✅ inventory.db seeded successfully.")

if __name__ == "__main__":
    seed()