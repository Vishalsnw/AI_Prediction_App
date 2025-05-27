from flask import Flask, render_template, jsonify
import wikipedia
import random
import requests
import feedparser
from newspaper import Article
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import json
import os

app = Flask(__name__)
predictions_data = []

RAPIDAPI_KEY = "a531e727f3msh281ef1f076f7139p198608jsn82cfb1c7b6d0"
COPILOT_URL = "https://copilot5.p.rapidapi.com/copilot"

def get_news_articles(topic, max_articles=3):
    query = topic.replace(" ", "+")
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN"
    feed = feedparser.parse(rss_url)
    full_texts = ""
    count = 0
    for entry in feed.entries:
        try:
            article = Article(entry.link)
            article.download()
            article.parse()
            full_texts += f"TITLE: {article.title}\n{article.text}\n\n"
            count += 1
        except:
            continue
        if count >= max_articles:
            break
    return full_texts or "No recent articles found."

def get_wikipedia_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=4)
    except:
        return "No Wikipedia info available."

def get_random_topics():
    return random.sample([
        "Ukraine war", "Stock market", "NASA", "Taiwan", "Elon Musk", "China", "AI regulations", 
        "Bitcoin", "Israel Gaza", "OPEC", "Modi", "Trump", "Meta", "Earthquake", "Houthi", 
        "Japan", "South China Sea", "North Korea", "Climate Change", "Cyber attack"
    ], 3)

def simulate_confidence_score(text):
    score = random.randint(85, 98)
    if "may" in text or "possible" in text:
        score -= 5
    return min(score, 99)

def generate_prediction(topic, news, wiki):
    astrology = random.choice([
        "Mars transit causing tension",
        "Mercury retrograde may cause disruption",
        "Saturn influence on economic shifts"
    ])

    prompt = f"""
You are an elite global forecaster with access to insider intelligence, news scans, forums, and astrology.

Your task: Predict one shocking or significant event that may happen TOMORROW. Mention specific names: companies, politicians, countries, or regions.

Sources:
- News Articles: {news}
- Wikipedia Summary: {wiki}
- Astrology Insight: {astrology}

Rules:
1. Predict ONLY if confident. Else respond: "Nothing significant to predict for tomorrow."
2. Format professionally, like a headline + structured paragraphs.
3. Use bold statements, thrilling tone, real names.

Now, generate a bold, headline-worthy forecast.
"""

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "copilot5.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY
    }

    payload = {
        "message": prompt,
        "conversation_id": None,
        "mode": "CHAT",
        "markdown": True
    }

    try:
        response = requests.post(COPILOT_URL, headers=headers, json=payload)
        result = response.json()
        return result['text'].strip()
    except Exception as e:
        return f"Error: {e}"

def update_predictions():
    global predictions_data
    predictions_data = []
    print(f"[{datetime.datetime.now()}] Updating predictions...")

    for topic in get_random_topics():
        news = get_news_articles(topic)
        wiki = get_wikipedia_summary(topic)
        result = generate_prediction(topic, news, wiki)

        if "nothing significant" in result.lower():
            continue

        confidence = simulate_confidence_score(result)
        if confidence >= 90:
            predictions_data.append({
                "topic": topic,
                "text": result,
                "confidence": confidence
            })

    print("Prediction update complete.")

@app.route("/")
def home():
    return render_template("index.html", predictions=predictions_data)

@app.route("/api/predictions")
def api_predictions():
    return jsonify(predictions_data)

# Schedule it to run daily
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_predictions, trigger="interval", hours=24)
scheduler.start()

# First run
update_predictions()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
