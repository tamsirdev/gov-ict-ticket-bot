import os
import re

CATEGORY_RULES = {
    "Hardware": [
        "printer",
        "keyboard",
        "monitor",
        "mouse",
        "screen",
        "laptop",
        "desktop",
        "hardware",
        "cable",
        "power",
        "charger",
        "battery",
        "usb",
        "port",
        "fan",
        "hard drive",
        "ssd",
        "ram",
        "broken",
        "physical",
        "device not turning",
    ],
    "Network": [
        "network",
        "wifi",
        "internet",
        "connection",
        "email not sending",
        "cannot browse",
        "online",
        "website",
        "vpn",
        "slow internet",
        "no signal",
        "lan",
        "ethernet",
        "dns",
        "ip address",
        "ping",
        "disconnected",
        "offline",
    ],
    "Account": [
        "password",
        "login",
        "lockout",
        "account",
        "access",
        "reset",
        "2fa",
        "authentication",
        "permission",
        "forgot",
        "credentials",
        "mfa",
        "sign in",
        "can't log",
        "unlock",
        "disabled account",
    ],
    "Software": [
        "software",
        "crash",
        "error",
        "install",
        "update",
        "blue screen",
        "bug",
        "app",
        "program",
        "windows",
        "linux",
        "mac",
        "office",
        "excel",
        "word",
        "outlook",
        "virus",
        "malware",
        "freeze",
        "unresponsive",
        "version",
        "upgrade",
        "patch",
        "driver",
    ],
}

PRIORITY_RULES = {
    "Critical": [
        "down",
        "outage",
        "emergency",
        "critical",
        "not working at all",
        "all users",
        "company-wide",
        "entire department",
        "cannot work",
        "system down",
        "deadline",
        "urgent",
    ],
    "High": [
        "important",
        "asap",
        "cannot",
        "unable",
        "stuck",
        "blocking",
        "soon",
        "error repeatedly",
        "multiple users",
        "escalate",
    ],
    "Low": [
        "question",
        "inquiry",
        "when",
        "how to",
        "minor",
        "slight",
        "cosmetic",
        "suggestion",
        "request",
        "future",
    ],
}


def _match_rules(text, rules):
    text_lower = text.lower()
    for label, keywords in rules.items():
        for kw in keywords:
            if re.search(re.escape(kw.lower()), text_lower):
                return label
    return None


def triage_issue_free(description):
    category = _match_rules(description, CATEGORY_RULES) or "General"
    priority = _match_rules(description, PRIORITY_RULES) or "Medium"
    return category, priority


def triage_issue(description):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return triage_issue_free(description)

    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    prompt = f"""
    You are an ICT Support AI. Analyze the following user issue and provide:
    1. Category (Hardware, Software, Network, or Account)
    2. Priority (Low, Medium, High, or Critical)

    Issue: "{description}"

    Return the result in format: Category | Priority
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        category, priority = result.split(" | ")
        return category, priority
    except Exception as e:
        print(f"AI Triage error ({e}), falling back to free triage")
        return triage_issue_free(description)
