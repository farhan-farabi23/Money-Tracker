import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "money_tracker.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@moneytracker.com",)
    ).fetchone()
    if existing:
        conn.close()
        return

    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@moneytracker.com", generate_password_hash("demo1234")),
    )
    conn.commit()

    user_id = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@moneytracker.com",)
    ).fetchone()["id"]

    sample_expenses = [
        (user_id, 42.50,  "Food",          "2026-05-01", "Weekly groceries"),
        (user_id, 12.00,  "Transport",     "2026-05-03", "Bus pass top-up"),
        (user_id, 95.00,  "Bills",         "2026-05-05", "Electricity bill"),
        (user_id, 30.00,  "Health",        "2026-05-08", "Pharmacy run"),
        (user_id, 15.99,  "Entertainment", "2026-05-12", "Streaming subscription"),
        (user_id, 60.00,  "Shopping",      "2026-05-15", "New trainers"),
        (user_id,  8.50,  "Food",          "2026-05-18", "Lunch out"),
        (user_id, 25.00,  "Other",         "2026-05-22", "Birthday gift"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        sample_expenses,
    )
    conn.commit()
    conn.close()
