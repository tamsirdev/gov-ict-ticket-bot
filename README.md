# Government ICT Service Ticket Bot (WhatsApp version)

This version of the bot uses **WhatsApp** via the **Twilio API**, which is much more common for government and public services in many regions.

## How it Works
1. **User Submission**: User sends a WhatsApp message.
2. **Webhook**: Twilio sends the message to our Flask application.
3. **AI Triage**: OpenAI categorizes and prioritizes the issue.
4. **Storage**: Data is saved in SQLite.

## Prerequisites
- A **Twilio Account** (Free trial works).
- An **OpenAI API Key**.
- **ngrok** (for local testing to expose your local port 5000 to the internet).

## Setup Instructions

1. **Twilio Sandbox Setup**:
   - Go to the Twilio Console -> Messaging -> Try it Out -> WhatsApp Sandbox.
   - Follow instructions to join the sandbox on your phone.
   - Set the Webhook URL to your ngrok URL (e.g., `https://your-id.ngrok-free.app/whatsapp`).

2. **Configure `.env`**:
   ```env
   OPENAI_API_KEY=your_openai_key
   TWILIO_ACCOUNT_SID=your_sid (optional for this simple version)
   TWILIO_AUTH_TOKEN=your_token (optional for this simple version)
   ```

3. **Run the Bot**:
   ```bash
   pip install -r requirements.txt
   python bot.py
   ```

4. **Expose with ngrok**:
   ```bash
   ngrok http 5000
   ```
   (Copy the forwarding URL into your Twilio Sandbox settings).

---
Developed for [Tamsir Njie's Portfolio](https://tamsirdev.github.io/Personal-Portfolio/)
