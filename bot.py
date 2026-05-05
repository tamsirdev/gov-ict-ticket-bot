import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from database import init_db, create_ticket, get_user_tickets
from ai_triage import triage_issue

load_dotenv()

app = Flask(__name__)

# Initialize DB on startup
init_db()

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    # Get message details from Twilio request
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '') # Format: whatsapp:+220XXXXXXX
    username = request.values.get('ProfileName', 'User')

    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg.lower() == 'status':
        # Handle status request
        tickets = get_user_tickets(sender_number)
        if not tickets:
            msg.body("🔍 You have no active tickets.")
        else:
            response_text = "🔍 *Your Tickets:*\n\n"
            for t in tickets:
                response_text += f"• #{t[0]} | Status: {t[1]} | {t[2]} ({t[3]})\n"
            msg.body(response_text)
            
    elif incoming_msg.lower() == 'start' or incoming_msg.lower() == 'hi':
        msg.body("👋 *Welcome to the Government ICT Support Bot.*\n\nPlease describe the technical issue you are facing in detail.")
        
    else:
        # Assume it's a new ticket description
        # 1. AI Triage
        category, priority = triage_issue(incoming_msg)
        
        # 2. Save to Database
        ticket_id = create_ticket(
            user_id=sender_number,
            username=username,
            description=incoming_msg,
            category=category,
            priority=priority
        )
        
        response_text = (
            f"✅ *Ticket Created!*\n\n"
            f"*Ticket ID:* #{ticket_id}\n"
            f"*Category:* {category}\n"
            f"*Priority:* {priority}\n\n"
            f"Our team has been notified. Type 'status' to check progress."
        )
        msg.body(response_text)

    return str(resp)

if __name__ == "__main__":
    # For local development, we run on port 5000
    app.run(port=5000)
