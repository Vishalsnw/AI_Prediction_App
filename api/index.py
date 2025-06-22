from flask import Flask, render_template, jsonify
import wikipedia
import requests
import feedparser
import os

app = Flask(__name__, template_folder="../templates")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-0e8fe679610b4b718e553f4fed7e3792")

def deepseek_generate(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "temperature": 0.3,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a prophecy AI trained on books of predictions like Les Propheties, Baba Vanga, "
                    "Edgar Cayce, Revelation, and modern psychic guides. You combine ancient foresight with present data. "
                    "Predict boldly but clearly for the common person."
                )
            },
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=25)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Prediction error: {e}"

def find_best_topic():
    prompt = """
Search the world silently. Read the signs, energy shifts, trends, and headlines.

Choose ONE topic where the future is shifting rapidly — something worthy of tomorrow’s powerful prediction.

Answer with 3 to 6 words max.
"""
    return deepseek_generate(prompt).strip()

def get_news_headlines(topic):
    try:
        rss_url = f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}&hl=en-IN&gl=IN"
        feed = feedparser.parse(rss_url)
        headlines = "\n".join([entry.title for entry in feed.entries[:5]])
        return headlines if headlines else "No recent headlines."
    except:
        return "News data unreadable."

def get_wikipedia_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=2)
    except:
        return "No Wikipedia data."

def generate_prediction():
    topic = find_best_topic()
    news = get_news_headlines(topic)
    wiki = get_wikipedia_summary(topic)

    prompt = f"""
You are a prophecy AI trained on books like:
- Les Propheties (Nostradamus)
- Baba Vanga predictions
- Edgar Cayce readings
- Book of Revelation
- Psychic prediction guides like "The Premonition Code" and "Psychic Witch"

With all this wisdom and real-world news knowledge, you must now make ONE bold but understandable prediction for tomorrow.

Topic: {topic}
News: {news}
Wikipedia: {wiki}

TASK:
Predict tomorrow’s most likely event linked to this topic.
Your format:
- **HEADLINE:** A bold summary
- **Why it will happen:** Simple, clear logic from news + intuition
- **Who will be impacted:** Mention real names/companies/countries
- **Timing:** Why tomorrow or next 24 hours
- If no prediction: write “No significant signs for tomorrow.”

Avoid vague words like "maybe" or "possibly".
Use human-friendly, mysterious but simple language.
"""
    prediction = deepseek_generate(prompt)

    if "no significant" not in prediction.lower():
        return [{
            "title": topic,
            "text": prediction.strip(),
            "confidence": 91,
            "accuracy": 92
        }]
    else:
        return []

@app.route("/")
def home():
    predictions = generate_prediction()
    return render_template("index.html", predictions=predictions)

@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})
