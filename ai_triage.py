import os
import openai

# You can replace this with a local model or another AI provider
def triage_issue(description):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "General", "Medium"

    openai.api_key = api_key
    
    prompt = f"""
    You are an ICT Support AI. Analyze the following user issue and provide:
    1. Category (Hardware, Software, Network, or Account)
    2. Priority (Low, Medium, High, or Critical)
    
    Issue: "{description}"
    
    Return the result in format: Category | Priority
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        category, priority = result.split(" | ")
        return category, priority
    except Exception as e:
        print(f"AI Triage error: {e}")
        return "General", "Medium"
