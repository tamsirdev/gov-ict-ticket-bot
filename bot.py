import functools
import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from ai_triage import triage_issue
from database import (
    create_ticket,
    get_all_tickets,
    get_user_tickets,
    init_db,
    update_ticket_status,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("bot")

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-change-in-production")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
VALID_STATUSES = ["Open", "In Progress", "Resolved", "Closed"]

init_db()

USE_TWILIO = os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN")

if USE_TWILIO:
    from twilio.twiml.messaging_response import MessagingResponse

# ── Health check (used by Docker / k8s) ────────────────────────────────


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ── Web UI (free, no API keys needed) ──────────────────────────────────


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit_ticket():
    username = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    description = request.form.get("description", "").strip()

    if not description:
        return render_template("index.html", error="Please describe your issue.")

    category, priority = triage_issue(description)
    ticket_id = create_ticket(phone, username, description, category, priority)
    return render_template(
        "ticket.html",
        ticket_id=ticket_id,
        category=category,
        priority=priority,
        username=username,
    )


@app.route("/status", methods=["GET", "POST"])
def check_status():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        return redirect(url_for("user_tickets", phone=phone))
    return render_template("status_form.html")


@app.route("/status/<phone>")
def user_tickets(phone):
    tickets = get_user_tickets(phone)
    return render_template("status.html", tickets=tickets, phone=phone)


# ── Admin dashboard ────────────────────────────────────────────────────


def admin_required(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return wrapped


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        error = "Wrong password"
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    status_filter = request.args.get("status", "")
    tickets = get_all_tickets()
    if status_filter:
        tickets = [t for t in tickets if t["status"] == status_filter]
    return render_template(
        "admin.html",
        tickets=tickets,
        statuses=VALID_STATUSES,
        current_filter=status_filter,
    )


@app.route("/admin/update/<int:ticket_id>", methods=["POST"])
@admin_required
def admin_update_status(ticket_id):
    new_status = request.form.get("status")
    if new_status in VALID_STATUSES:
        update_ticket_status(ticket_id, new_status)
    return redirect(url_for("admin_dashboard", status=request.args.get("status", "")))


# ── WhatsApp / Twilio webhook (paid, requires API keys) ────────────────


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender_number = request.values.get("From", "")
    username = request.values.get("ProfileName", "User")

    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg.lower() in ("status", "check"):
        tickets = get_user_tickets(sender_number)
        if not tickets:
            msg.body("You have no active tickets.")
        else:
            lines = ["*Your Tickets:*"]
            for t in tickets:
                lines.append(f"- #{t[0]} | Status: {t[1]} | {t[2]} ({t[3]})")
            msg.body("\n".join(lines))

    elif incoming_msg.lower() in ("start", "hi", "hello"):
        msg.body(
            "Welcome to the Government ICT Support Bot.\n\n"
            "Describe your technical issue and a ticket will be created.\n"
            "Reply 'status' to check your tickets."
        )

    else:
        category, priority = triage_issue(incoming_msg)
        ticket_id = create_ticket(
            sender_number, username, incoming_msg, category, priority
        )
        msg.body(
            f"Ticket #{ticket_id} created!\n"
            f"Category: {category}\n"
            f"Priority: {priority}\n\n"
            "Reply 'status' for updates."
        )

    return str(resp)


if __name__ == "__main__":
    mode = "FREE (web UI)" if not USE_TWILIO else "web UI + WhatsApp"
    log.info("Starting in %s mode on port 5000", mode)
    app.run(port=5000, debug=True)  # noqa: S201
