# === File: api/index.py ===
from flask import Flask, render_template, jsonify
import wikipedia
import requests
import feedparser
import os

app = Flask(__name__, template_folder="../templates")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-0e8fe679610b4b718e553f4fed7e3792")

# --- Helper: Ask DeepSeek ---
def deepseek_generate(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "You are a mystical prediction engine with powers of Nostradamus and Baba Vanga. You foresee very specific future events."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=20)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Prediction error: {e}"

# --- Dynamic Topic Selection ---
def find_best_topic():
    prompt = """
    TASK: Scan global tensions, disasters, and events. Pick ONE high-impact topic for tomorrow.
    FORMAT: Return only the topic in 5 words or less. Do NOT include any explanation.
    """
    return deepseek_generate(prompt).strip()

# --- Context Collection ---
def get_news_headlines(topic):
    try:
        url = f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}&hl=en-IN&gl=IN"
        feed = feedparser.parse(url)
        return "\n".join([entry.title for entry in feed.entries[:5]]) or "No recent headlines."
    except:
        return "No recent headlines."

def get_wikipedia_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=2)
    except:
        return "No Wikipedia info."

# --- Prophecy Generation ---
def generate_prediction():
    topic = find_best_topic()
    headlines = get_news_headlines(topic)
    wiki = get_wikipedia_summary(topic)

    prompt = f"""
TOPIC: {topic}

TASK: Predict a clear, specific, and shocking event that may occur TOMORROW.
Use these:
- News headlines: {headlines}
- Wikipedia summary: {wiki}

Rules:
- Begin with a prophecy-style HEADLINE.
- Describe clearly what may happen, where, and to whom.
- Use powerful, mystical, or symbolic tones, like Nostradamus.
- Mention real countries, people, companies, or cities.
- End with celestial sign or timing.
- If no prediction possible, say: "Nothing significant to predict tomorrow."
"""
    text = deepseek_generate(prompt)

    if "nothing significant" in text.lower():
        return []
    else:
        return [{
            "headline": text.split("\n")[0].strip("* "),
            "reasoning": "\n".join(text.split("\n")[1:]).strip(),
            "confidence": 91
        }]

# --- Routes ---
@app.route("/")
def home():
    predictions = generate_prediction()
    return render_template("index.html", predictions=predictions)

@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})
    
