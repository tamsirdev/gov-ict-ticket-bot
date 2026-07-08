import os
import sqlite3

from database import (
    create_ticket,
    get_all_tickets,
    get_user_tickets,
    update_ticket_status,
)


def test_init_db_creates_table():
    conn = sqlite3.connect(os.environ["DB_NAME"])
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'")
    assert cursor.fetchone() is not None


def test_create_and_retrieve_ticket():
    tid = create_ticket("+220test", "Test", "Something broke", "Software", "High")
    assert tid == 1

    tickets = get_user_tickets("+220test")
    assert len(tickets) == 1
    assert tickets[0]["status"] == "Open"
    assert tickets[0]["category"] == "Software"


def test_get_all_tickets():
    create_ticket("+220a", "A", "Issue 1", "Network", "Low")
    create_ticket("+220b", "B", "Issue 2", "Hardware", "Critical")

    all_tickets = get_all_tickets()
    assert len(all_tickets) == 2


def test_get_user_tickets_empty():
    tickets = get_user_tickets("+220nonexistent")
    assert tickets == []


def test_update_ticket_status():
    tid = create_ticket("+220u", "U", "Test issue", "General", "Medium")

    updated = update_ticket_status(tid, "In Progress")
    assert updated is True

    tickets = get_user_tickets("+220u")
    assert tickets[0]["status"] == "In Progress"


def test_update_nonexistent_ticket():
    updated = update_ticket_status(999, "Resolved")
    assert updated is False
