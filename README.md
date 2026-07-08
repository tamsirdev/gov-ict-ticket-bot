# Government ICT Service Ticket Bot

A smart helpdesk system for government ICT departments. Citizens submit issues via a web form (or WhatsApp), the bot auto-categorizes and priorities them, and ICT officers manage tickets through an admin dashboard.

**No API keys required to run** — works immediately with built-in rule-based triage and a web UI. OpenAI and WhatsApp/Twilio can be enabled later as upgrades.

---

## Features

- **Web portal** — Submit tickets and check status from any browser
- **WhatsApp support** *(optional, requires Twilio)* — Submit tickets via WhatsApp
- **Smart triage** — AI-powered (OpenAI) or free rule-based categorization: Hardware, Software, Network, Account
- **Priority assignment** — Auto-tags tickets as Critical, High, Medium, or Low
- **Admin dashboard** — View, filter, and update ticket statuses
- **Persistent storage** — SQLite database, no external services needed
- **Containerized** — Docker & Docker Compose support
- **CI/CD** — GitHub Actions pipeline: lint, test, build

---

## Quick Start

```bash
git clone https://github.com/tamsirdev/gov-ict-ticket-bot.git
cd gov-ict-ticket-bot

# Run without any API keys
pip install -r requirements.txt
python bot.py
```

Open **http://localhost:5000** — you're ready to submit tickets.

### With Docker

```bash
docker compose up
```

Visit **http://localhost:5000**.

---

## How It Works

```
Citizen → Web Form → Flask App → Triage Engine → SQLite → Admin Dashboard
                                    │
                                ┌───┴───┐
                            Free AI    OpenAI
                        (rule-based)   (paid key)
```

1. A citizen describes their issue via the web form
2. The triage engine categorizes and priorities it
3. The ticket is saved to the database
4. The citizen gets a confirmation with their ticket number
5. ICT officers manage tickets in the admin dashboard at `/admin`

---

## User Guide

### Submitting a Ticket

1. Open the app in your browser
2. Enter your name, phone number, and describe the issue
3. Click **Submit Ticket** — you'll receive a ticket ID
4. Save the ID to check status later

### Checking Ticket Status

- Click **Check Existing Ticket Status** on the home page
- Enter your phone number to see all your tickets

### Admin Dashboard

- Visit **/admin** and log in (default password: `admin`)
- View all tickets sorted by priority
- Filter by status (Open, In Progress, Resolved, Closed)
- Update ticket statuses as work progresses

---

## Upgrading to Paid Features

| Feature | Free | With API Key |
|---------|------|-------------|
| Triage | Rule-based keywords | OpenAI GPT-3.5 |
| Interface | Web UI only | Web UI + WhatsApp |
| Cost | Free | OpenAI & Twilio usage |

### Enable OpenAI Triage

```env
OPENAI_API_KEY=sk-your-key-here
```

### Enable WhatsApp

```env
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
```

Then set your Twilio sandbox webhook to `https://your-url/whatsapp`.

---

## Project Structure

```
├── bot.py              # Flask application (routes, web UI, admin, webhook)
├── ai_triage.py        # Triage engine (free rule-based + OpenAI fallback)
├── database.py         # SQLite database layer
├── templates/          # HTML templates
│   ├── index.html
│   ├── ticket.html
│   ├── status_form.html
│   ├── status.html
│   ├── admin.html
│   └── admin_login.html
├── tests/              # Pytest test suite
├── Dockerfile          # Production container (gunicorn, multi-stage)
├── docker-compose.yml  # One-command deployment
├── .github/workflows/  # CI/CD pipeline
└── pyproject.toml       # Ruff & pytest config
```

---

**Developed by Tamsir Njie** · [Portfolio](https://tamsirdev.github.io/Personal-Portfolio/)
