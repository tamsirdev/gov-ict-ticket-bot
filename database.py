import sqlite3
from datetime import datetime

DB_NAME = "tickets.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO tickets (user_id, username, issue_description, category, priority, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, description, category, priority))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ticket_id

def get_user_tickets(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, status, category, created_at FROM tickets WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
