import os
import sqlite3
from datetime import datetime


def _db_path():
    return os.getenv("DB_NAME", "tickets.db")


def init_db():
    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            username TEXT,
            issue_description TEXT NOT NULL,
            category TEXT,
            priority TEXT,
            status TEXT DEFAULT 'Open',
            created_at DATETIME
        )
    ''')
    conn.commit()
    conn.close()


def create_ticket(user_id, username, description, category, priority):
    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO tickets (user_id, username, issue_description, "
        "category, priority, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, username, description, category, priority, created_at),
    )
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ticket_id


def get_user_tickets(user_id):
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, status, category, created_at FROM tickets WHERE user_id = ?",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_tickets():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, username, issue_description, "
        "category, priority, status, created_at "
        "FROM tickets ORDER BY "
        "CASE priority WHEN 'Critical' THEN 0 WHEN 'High' THEN 1 "
        "WHEN 'Medium' THEN 2 ELSE 3 END, created_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_ticket_status(ticket_id, new_status):
    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute('UPDATE tickets SET status = ? WHERE id = ?', (new_status, ticket_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0
