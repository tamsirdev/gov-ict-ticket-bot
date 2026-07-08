# Technical Documentation — Government ICT Service Ticket Bot

## 1. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      User Layer                          │
│   ┌──────────────┐    ┌─────────────────────────────┐   │
│   │  Web Browser │    │  WhatsApp (optional/Twilio) │   │
│   └──────┬───────┘    └──────────────┬──────────────┘   │
│          │                           │                   │
├──────────┼───────────────────────────┼───────────────────┤
│          │         Application Layer │                   │
│   ┌──────┴───────────────────────────┴──────────────┐   │
│   │            Flask Web Server (bot.py)             │   │
│   │  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │   │
│   │  │  Web UI  │  │  Admin   │  │ WhatsApp Hook │  │   │
│   │  └────┬─────┘  └────┬─────┘  └──────┬────────┘  │   │
│   └───────┼──────────────┼───────────────┼───────────┘   │
│           │              │               │               │
├───────────┼──────────────┼───────────────┼───────────────┤
│           │    Service Layer              │               │
│    ┌──────┴───────────────────────────────┴──────────┐   │
│    │           Triage Engine (ai_triage.py)           │   │
│    │  ┌─────────────────┐    ┌────────────────────┐  │   │
│    │  │  Free (rules)   │    │  OpenAI (GPT-3.5)  │  │   │
│    │  │  No API key     │    │  Requires key      │  │   │
│    │  └────────┬────────┘    └─────────┬──────────┘  │   │
│    └───────────┼───────────────────────┼──────────────┘   │
│                │                       │                   │
│         ┌──────┴───────────────────────┴──────────────┐   │
│         │         Database (database.py)              │   │
│         │              SQLite                          │   │
│         └─────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Components

| Component | File | Purpose |
|-----------|------|---------|
| Flask App | `bot.py` | HTTP routes, web UI, admin dashboard, WhatsApp webhook |
| Triage Engine | `ai_triage.py` | Categorizes + priorities issues (keyword rules or OpenAI) |
| Database | `database.py` | SQLite CRUD operations for tickets |
| Templates | `templates/` | Jinja2 HTML pages |
| Tests | `tests/` | Pytest suite (27 tests) |

---

## 2. Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.9+ |
| Web Framework | Flask 3.x |
| Templates | Jinja2 |
| Database | SQLite 3 |
| Production Server | Gunicorn |
| Container | Docker (multi-stage build) |
| Orchestration | Docker Compose |
| CI/CD | GitHub Actions |
| Linting | Ruff |
| Testing | Pytest |
| AI Triage | OpenAI GPT-3.5-Turbo (optional) |
| WhatsApp | Twilio API (optional) |

---

## 3. API Reference

### Web Routes

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/` | No | Home page / ticket submission form |
| POST | `/submit` | No | Submit a new ticket |
| GET | `/status` | No | Ticket status lookup form |
| GET | `/status/<phone>` | No | View tickets for a phone number |
| GET | `/health` | No | Health check (returns JSON `{"status": "ok"}`) |
| GET | `/admin/login` | No | Admin login page |
| POST | `/admin/login` | No | Authenticate admin |
| GET | `/admin/logout` | Yes | Log out |
| GET | `/admin` | Yes | Admin dashboard (with optional `?status=` filter) |
| POST | `/admin/update/<id>` | Yes | Update a ticket's status |
| POST | `/whatsapp` | No* | Twilio WhatsApp webhook |

*\* WhatsApp webhook is only available when Twilio credentials are configured.*

### Health Check

```
GET /health
→ 200 {"status": "ok"}
```

Used by Docker `HEALTHCHECK` and container orchestration.

---

## 4. Database Schema

**Table: `tickets`**

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER (PK) | auto | Auto-incrementing ticket ID |
| user_id | TEXT | — | Phone number or user identifier |
| username | TEXT | — | Display name |
| issue_description | TEXT | — | Raw issue text from user |
| category | TEXT | — | Hardware, Software, Network, Account, General |
| priority | TEXT | — | Critical, High, Medium, Low |
| status | TEXT | `'Open'` | Open, In Progress, Resolved, Closed |
| created_at | DATETIME | — | Timestamp of submission |

Queries are ordered by priority (Critical → High → Medium → Low) then by newest first.

---

## 5. Triage Engine

### Free Mode (Rule-Based)

Keyword matching with `re.search()` against defined dictionaries:

**Categories:**
- **Hardware** — printer, keyboard, monitor, mouse, laptop, cable, charger, battery, usb, broken, physical, ...
- **Network** — wifi, internet, connection, vpn, dns, ethernet, ping, offline, ...
- **Account** — password, login, lockout, reset, 2fa, mfa, authentication, credentials, ...
- **Software** — crash, error, install, update, bug, app, program, office, excel, virus, ...
- **General** — fallback if no keywords match

**Priorities:**
- **Critical** — down, outage, emergency, not working at all, all users, company-wide
- **High** — important, asap, cannot, unable, stuck, blocking, escalate
- **Medium** — default
- **Low** — question, inquiry, how to, minor, suggestion, cosmetic

### OpenAI Mode

When `OPENAI_API_KEY` is set, uses GPT-3.5-Turbo with a prompt instructing it to return `Category | Priority`. Falls back to rule-based triage on API error.

---

## 6. DevOps & CI/CD

### CI Pipeline (`.github/workflows/ci.yml`)

```
push/PR → main
  │
  ├─ lint (ruff check)
  │
  ├─ test (pytest -v)
  │      ├─ test_triage.py (9 tests)
  │      ├─ test_database.py (6 tests)
  │      └─ test_routes.py (12 tests)
  │
  └─ build (docker build + docker compose build)
```

All stages must pass for a PR to merge.

### Dockerfile

- **Multi-stage build**: builder stage installs pip packages, runtime stage copies only what's needed
- **Non-root user**: runs as `app` user (not root)
- **Production server**: uses Gunicorn with 4 workers
- **Health check**: pings `/health` every 30 seconds

```dockerfile
# Build
FROM python:3.9-slim AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime
FROM python:3.9-slim
COPY --from=builder /root/.local /root/.local
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "bot:app"]
```

### Docker Compose

```yaml
services:
  app:
    build: .
    ports: ["5000:5000"]
    volumes: ["tickets_data:/app/tickets.db"]
    healthcheck: ...
```

Run: `docker compose up`

### Local Development

```bash
# Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run
python bot.py

# Lint
ruff check .

# Test
pytest -v
```

---

## 7. Configuration

All configuration via environment variables (`.env` file or container env):

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `OPENAI_API_KEY` | — | No | Enables GPT-3.5 triage |
| `TWILIO_ACCOUNT_SID` | — | No | Enables WhatsApp webhook |
| `TWILIO_AUTH_TOKEN` | — | No | Twilio auth |
| `ADMIN_PASSWORD` | `admin` | No | Admin dashboard password |
| `FLASK_SECRET` | `dev-...` | No | Flask session secret key |
| `DB_NAME` | `tickets.db` | No | SQLite file path |

---

## 8. WhatsApp Integration (Twilio)

When Twilio credentials are present in `.env`:

1. The app serves a webhook at `POST /whatsapp`
2. Twilio sends incoming WhatsApp messages to this endpoint
3. The bot parses the message, runs triage, creates a ticket, and replies
4. Users can text `status` to check their tickets

**Setup:**
- Configure your Twilio WhatsApp Sandbox webhook URL to `https://your-domain/whatsapp`
- For local testing, use ngrok: `ngrok http 5000`

---

## 9. Testing

27 tests across three test files:

```
tests/
├── conftest.py          # Fixtures: temp DB, Flask client, sample tickets
├── test_triage.py       # 9 tests — all categories & priorities
├── test_database.py     # 6 tests — CRUD, edge cases
└── test_routes.py       # 12 tests — web UI, admin auth, status updates
```

Each test gets an isolated temporary SQLite database. The Flask app is tested using Werkzeug's test client (no live server needed).

Run: `pytest -v` (verbose) or `pytest` (quiet).

---

## 10. Security Notes

- Admin dashboard uses session-based auth (signed Flask cookies)
- Default `ADMIN_PASSWORD` should be changed in production
- Set a strong `FLASK_SECRET` in production
- The Docker container runs as a non-root user
- `.env` is gitignored — secrets never committed
- No user input is eval'd or executed

---

## 11. Project Roadmap

- [x] Web UI ticket submission
- [x] Free rule-based triage
- [x] Admin dashboard
- [x] Docker + Docker Compose
- [x] CI/CD pipeline
- [x] Test suite
- [ ] Email notifications
- [ ] SMS alerts (Twilio SMS)
- [ ] User authentication
- [ ] SLA tracking & escalations
- [ ] Reporting / analytics

---

**Project Lead:** Tamsir Njie  
**Repository:** https://github.com/tamsirdev/gov-ict-ticket-bot  
**Category:** DevOps & AI Automation
