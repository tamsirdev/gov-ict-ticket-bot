---
marp: true
theme: uncover
class: lead
paginate: true
backgroundColor: #1a202c
color: white
style: |
  section { font-family: -apple-system, 'Segoe UI', sans-serif; }
  h1 { color: #63b3ed; }
  h2 { color: #90cdf4; }
  h3 { color: #b2d4ff; }
  a { color: #63b3ed; }
  code { background: #2d3748; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
  .columns { display: flex; gap: 24px; }
  .columns div { flex: 1; }
  .tag { display: inline-block; background: #2d3748; padding: 2px 10px; border-radius: 12px; font-size: 0.7em; margin: 2px; }
  .tag-green { background: #276749; }
  .tag-blue { background: #2b6cb0; }
  .tag-red { background: #9b2c2c; }
---

# Government ICT Service Ticket Bot

Automated Helpdesk with AI Triage & DevOps Pipeline

**Tamsir Njie**

---

## The Problem

- **ICT helpdesks in government** are overwhelmed with manual ticket handling
- Citizens struggle to **find the right channel** to report issues
- ICT officers waste time **categorizing and prioritizing** tickets manually
- No **automated tracking** — tickets get lost in emails and phone calls

> "A citizen's printer has been down for two weeks because the ticket was never logged."

---

## The Solution

<div class="columns">
<div>

### For Citizens
- Submit issues via **web browser** or **WhatsApp**
- Get instant **ticket ID & confirmation**
- Check status anytime

</div>
<div>

### For ICT Officers
- **Admin dashboard** with all tickets in one place
- Auto-categorized issues (Hardware, Software, Network, Account)
- Priority-assigned — Critical issues surface first

</div>
</div>

---

## System Architecture

```
                    ┌──────────────────┐
                    │   Web Browser    │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Flask App      │
                    │   (bot.py)       │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌──────▼──────┐  ┌────▼────────┐
     │  Triage     │  │  Database   │  │  Admin      │
     │  Engine     │  │  (SQLite)   │  │  Dashboard  │
     │  AI / Rules │  │             │  │             │
     └─────────────┘  └─────────────┘  └─────────────┘
```

Optionally: WhatsApp (Twilio) + OpenAI triage

---

## Key Features

| Feature | Free Mode | Paid Upgrade |
|---------|-----------|-------------|
| Ticket submission | Web form | + WhatsApp |
| Triage engine | Rule-based keywords | OpenAI GPT-3.5 |
| Admin dashboard | ✓ | ✓ |
| Status tracking | ✓ | ✓ |
| Docker support | ✓ | ✓ |
| CI/CD pipeline | ✓ | ✓ |
| **Cost** | **$0** | OpenAI + Twilio usage |

---

## Tech Stack

<div class="columns">
<div>

### Backend
- **Python 3.9+**
- **Flask** web framework
- **SQLite** database
- **Jinja2** templates
- **Gunicorn** production server

### DevOps
- **Docker** + Docker Compose
- **GitHub Actions** CI/CD
- **Ruff** linting
- **Pytest** test suite

</div>
<div>

### AI & APIs
- **OpenAI GPT-3.5** (optional)
- **Twilio WhatsApp** (optional)

### Frontend
- HTML / CSS
- Responsive design
- Dark admin theme

</div>
</div>

---

## How It Works — Flow

```
1. User describes issue
         │
2. Triage Engine analyzes text
         │
   ┌─────┴─────┐
   │  Free     │  OpenAI (if key set)
   │  Keywords │  GPT-3.5
   └─────┬─────┘
         │
3. Category + Priority assigned
         │
4. Ticket saved to SQLite
         │
5. User gets confirmation (ID #)
         │
6. Admin views & updates status
```

---

## DevOps Pipeline

```yaml
# .github/workflows/ci.yml
on: push → main

jobs:
  lint:    ruff check .
  test:    pytest -v
  build:   docker build + docker compose build
```

- **27 automated tests** — triage, database, routes, auth
- **Ruff linting** — import sorting, security checks, style
- **Docker multi-stage build** — slim production image
- **Health checks** — `/health` endpoint for orchestration
- **Docker Compose** — one-command deployment

---

## Admin Dashboard

```
/admin ─────────────────────────────────────┐
│  Ticket Dashboard                [Logout] │
│                                            │
│  [All] [Open] [In Progress] [Resolved] [Closed]
│                                            │
│  ┌────────────────────────────────────┐   │
│  │ #3  🔴 Critical  Network          │   │
│  │    Aminata · +220555....          │   │
│  │    "WiFi keeps dropping every hr"  │   │
│  │                          [▼ Open] │   │
│  └────────────────────────────────────┘   │
│  ┌────────────────────────────────────┐   │
│  │ #1  🟡 High  Hardware             │   │
│  │    Musa · +220555....              │   │
│  │    "Monitor screen is flickering"  │   │
│  │                    [▼ In Progress] │   │
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

---

## Database Schema

```sql
CREATE TABLE tickets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL,
    username    TEXT,
    issue_description TEXT NOT NULL,
    category    TEXT,      -- Hardware | Software | Network | Account
    priority    TEXT,      -- Critical | High | Medium | Low
    status      TEXT DEFAULT 'Open',
    created_at  DATETIME
);
```

Ordered by: `Critical → High → Medium → Low`, then newest first.

---

## Triage Engine — Free Mode

Keyword matching — no API key required:

| Category | Triggers |
|----------|----------|
| **Hardware** | printer, keyboard, monitor, mouse, laptop, cable, broken |
| **Network** | wifi, internet, connection, vpn, dns, offline |
| **Account** | password, login, reset, 2fa, authentication |
| **Software** | crash, error, install, update, bug, virus |
| **General** | *(fallback if no match)* |

| Priority | Triggers |
|----------|----------|
| **Critical** | down, outage, emergency, not working, company-wide |
| **High** | important, asap, cannot, stuck, blocking |
| **Medium** | *(default)* |
| **Low** | question, inquiry, how to, minor, suggestion |

---

## Triage Engine — OpenAI Mode

**When `OPENAI_API_KEY` is set:**

```
Prompt: "You are an ICT Support AI. Analyze the following
         user issue and provide: 1. Category (Hardware,
         Software, Network, or Account) 2. Priority (Low,
         Medium, High, or Critical)

         Issue: 'My computer won't boot up'

         Return: Category | Priority"

Response: "Hardware | Critical"
```

Falls back to rule-based triage on API error.

---

## Project Structure

```
├── bot.py              # Flask app (routes, admin, webhook)
├── ai_triage.py        # Triage engine (rules + OpenAI)
├── database.py         # SQLite layer
├── templates/          # 6 HTML templates
├── tests/              # 27 pytest tests
├── Dockerfile          # Multi-stage production build
├── docker-compose.yml  # One-command deploy
├── .github/workflows/  # CI/CD pipeline
├── pyproject.toml      # Ruff + pytest config
└── .env.example        # Env var template
```

---

## Running the Project

### No API keys — runs immediately:

```bash
pip install -r requirements.txt
python bot.py
# → http://localhost:5000
```

### With Docker:

```bash
docker compose up
# → http://localhost:5000
```

### Admin dashboard:
- **URL:** `/admin`
- **Password:** `admin` (change via `ADMIN_PASSWORD` env var)

---

## Demo Walkthrough

```
1. Open http://localhost:5000
         │
2. Enter: Name, Phone, Issue
         │
3. Click "Submit Ticket"
         │
   ┌─────▼─────┐
   │  ✅       │  Ticket Created!
   │  #3       │  Hardware | Critical
   └───────────┘
         │
4. Visit /admin → login → see ticket
         │
5. Change status: Open → In Progress
         │
6. Visit /status → enter phone → see updates
```

---

## Future Roadmap

- **Email notifications** — alert users when status changes
- **SMS alerts** — via Twilio SMS (existing account)
- **User authentication** — role-based access (citizen vs admin)
- **SLA tracking** — auto-escalate if ticket exceeds time limit
- **Reporting** — weekly PDF reports for management
- **Attachments** — allow screenshots in tickets
- **Multi-language** — support local languages (Wolof, Mandinka, etc.)

---

## What This Project Demonstrates

| Skill | Evidence |
|-------|----------|
| **Full-stack development** | Flask web app with HTML/CSS templates |
| **API integration** | OpenAI & Twilio (with graceful fallback) |
| **Database design** | SQLite schema, CRUD, query optimization |
| **DevOps** | Docker, CI/CD, testing, linting |
| **AI/ML** | GPT-3.5 integration + rule-based engine |
| **UX design** | Admin dashboard, responsive web forms |
| **Security** | Session auth, non-root container, env isolation |

---

# Thank You

**Government ICT Service Ticket Bot**

![q](https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://github.com/tamsirdev/gov-ict-ticket-bot)

**GitHub:** [github.com/tamsirdev/gov-ict-ticket-bot](https://github.com/tamsirdev/gov-ict-ticket-bot)

---

*Built with Python, Flask, Docker, and GitHub Actions*
