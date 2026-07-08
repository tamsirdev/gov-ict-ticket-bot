import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_triage import triage_issue_free
from database import create_ticket, init_db


@pytest.fixture(autouse=True)
def _db():
    """Use a temporary database for every test."""
    tmp = tempfile.mkstemp(suffix=".db")
    os.environ["DB_NAME"] = tmp[1]
    os.close(tmp[0])
    init_db()
    yield
    os.unlink(os.environ["DB_NAME"])


@pytest.fixture
def app():
    from bot import app as _app

    _app.config["TESTING"] = True
    _app.config["SECRET_KEY"] = "testing"  # noqa: S105
    return _app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_tickets(_db):
    ids = []
    for desc, name in [
        ("WiFi keeps dropping every hour", "Fatou"),
        ("Monitor screen is flickering", "Musa"),
        ("Cannot login to email account", "Aminata"),
    ]:
        cat, pri = triage_issue_free(desc)
        tid = create_ticket(f"+220{name}", name, desc, cat, pri)
        ids.append(tid)
    return ids
