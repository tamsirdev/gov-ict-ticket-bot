# Project Documentation: Government ICT Service Ticket Bot (WhatsApp)

## 1. Overview
The Government ICT Service Ticket Bot is an automated helpdesk solution designed to streamline technical support requests within government departments. By leveraging WhatsApp as the user interface and AI for automatic categorization, it reduces the administrative burden on ICT officers.

## 2. System Architecture
The system consists of four main components:
*   **User Interface (WhatsApp):** Users interact with the system via a familiar messaging app.
*   **API Gateway (Twilio):** Acts as the bridge between WhatsApp and our application.
*   **Application Server (Flask):** The core logic that handles incoming messages and coordinates between the database and AI.
*   **AI Engine (OpenAI):** Performs "Ticket Triage" by analyzing the user's natural language description.
*   **Database (SQLite):** A persistent store for all tickets and their statuses.

## 3. Technical Stack
*   **Language:** Python 3.9+
*   **Web Framework:** Flask
*   **Database:** SQLite3
*   **Cloud APIs:** Twilio (WhatsApp), OpenAI (GPT-3.5-Turbo)
*   **Environment Management:** Python-dotenv
*   **DevOps:** Docker

## 4. Setup & Installation

### Step 1: External Services
1.  **OpenAI:** Generate an API key from the [OpenAI Platform](https://platform.openai.com/).
2.  **Twilio:** 
    *   Create a free account at [Twilio](https://www.twilio.com/).
    *   Navigate to **Messaging > Try it Out > WhatsApp Sandbox**.
    *   Link your phone to the sandbox by sending the unique code provided to the Twilio number.

### Step 2: Local Environment
1.  **Clone the project** to your local machine.
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=your_key_here
    # Note: Twilio SID/Token are not strictly required for sandbox webhooks but good for production
    ```

### Step 3: Tunneling with ngrok
Since Twilio needs to send data to your local computer, you must use a tunnel:
1.  Download and install **ngrok**.
2.  Run the tunnel: `ngrok http 5000`
3.  Copy the `Forwarding` URL (e.g., `https://a1b2-c3d4.ngrok.io`).
4.  In the Twilio Sandbox settings, paste this URL into the **"When a message comes in"** field and append `/whatsapp`. 
    *Example:* `https://a1b2-c3d4.ngrok.io/whatsapp`

## 5. Usage
1.  **Start the application:** `python bot.py`
2.  **Send a message:** Open the WhatsApp conversation with the Twilio number.
3.  **Commands:**
    *   `Hi` or `Start`: Displays the welcome message.
    *   `Status`: Lists all your submitted tickets.
    *   *[Any other text]*: Automatically creates a new ticket. The AI will categorize it (e.g., "Software") and assign a priority (e.g., "High").

## 6. Developer Notes (For Portfolio)
This project demonstrates the following high-level engineering skills:
*   **Automation:** Solving real-world inefficiency through code.
*   **API Integration:** Successfully connecting multiple third-party services (Twilio & OpenAI).
*   **Asynchronous Thinking:** Handling webhooks and stateless communication.
*   **Data Integrity:** Using a relational database to maintain state.

---
**Project Lead:** Tamsir Njie
**Category:** DevOps & AI Automation
