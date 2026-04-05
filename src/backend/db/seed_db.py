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
            (sku, name, category_id, supplier_id, unit_price, stock_qty, reorder_level)
        VALUES (?,?,?,?,?,?,?)
    """, [
        ("EL-001", "Wireless Mouse",        1, 1, 499.00,  45, 10),
        ("EL-002", "Mechanical Keyboard",   1, 1, 1899.00, 20, 5),
        ("EL-003", "USB-C Hub 7-in-1",      1, 1, 1299.00, 12, 8),
        ("ST-001", "A4 Notebook (Pack 5)",  2, 2, 149.00,  80, 20),
        ("ST-002", "Ball Pen Box (50pcs)",  2, 2,  99.00,  60, 15),
        ("FU-001", "Ergonomic Chair",       3, 3, 8999.00,  8,  2),
        ("FU-002", "Standing Desk",         3, 3,15999.00,  4,  2),
        ("AP-001", "Company T-Shirt (M)",   4, 2, 399.00,  30, 10),
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

    conn.commit()
    conn.close()
    print("✅ inventory.db seeded successfully.")

if __name__ == "__main__":
    seed()