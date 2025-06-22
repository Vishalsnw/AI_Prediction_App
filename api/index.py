from flask import Flask, render_template, jsonify
import wikipedia
import requests
import feedparser
import datetime
import os

app = Flask(__name__, template_folder="../templates")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-0e8fe679610b4b718e553f4fed7e3792")  # Add your key here or from Vercel Env Vars

TOPICS = [
    "China Taiwan conflict", "Middle East oil crisis", "India elections",
    "US Federal Reserve", "Nvidia stock", "Artificial Intelligence laws",
    "Bitcoin regulation", "SpaceX launch", "Cyberwarfare", "Nuclear threat"
]

def get_news_headlines(topic):
    try:
        rss_url = f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}&hl=en-IN&gl=IN"
        feed = feedparser.parse(rss_url)
        return "\n".join([f"{entry.title}" for entry in feed.entries[:3]]) or "No recent headlines found."
    except:
        return "No headlines available."

def get_wikipedia_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=3)
    except:
        return "No Wikipedia summary available."

def generate_prediction(topic):
    news = get_news_headlines(topic)
    wiki = get_wikipedia_summary(topic)

    prompt = f"""
You are a geopolitical and financial prediction expert.

TASK: Predict one highly likely and impactful event that may happen TOMORROW related to the topic: "{topic}".

Use these sources:
- News headlines: {news}
- Wikipedia: {wiki}

Rules:
- Start with a bold HEADLINE.
- Add structured, brief reasoning.
- Mention real people, places, or companies.
- Avoid vague terms like "maybe" or "possibly".
- If no prediction, say: "Nothing significant to predict for tomorrow."
"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": "You are an accurate forecaster."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        res = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Prediction error: {e}"

@app.route("/")
def home():
    predictions_data = []
    for topic in TOPICS:
        result = generate_prediction(topic)
        if "nothing significant" not in result.lower():
            predictions_data.append({
                "title": topic,
                "text": result,
                "confidence": 90,
                "accuracy": 90
            })
    return render_template("index.html", predictions=predictions_data)

@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})

# DO NOT define `handler` or `main()` — let Vercel pick `app` itself
