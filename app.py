from flask import Flask, render_template, jsonify
import wikipedia
import requests
import feedparser
from newspaper import Article
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import json
import os

app = Flask(__name__)
predictions_data = []

# --- Config ---
DEEPSEEK_API_KEY = "sk-0e8fe679610b4b718e553f4fed7e3792"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# --- Topics (Fixed, No Randomness) ---
TOPICS = [
    "China Taiwan conflict", "Middle East oil crisis", "India elections",
    "US Federal Reserve", "Nvidia stock", "Artificial Intelligence laws",
    "Bitcoin regulation", "SpaceX launch", "Cyberwarfare", "Nuclear threat"
]

# --- News ---
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

# --- Wikipedia ---
def get_wikipedia_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=4)
    except:
        return "No Wikipedia info available."

# --- DeepSeek Prediction ---
def generate_prediction(topic, news, wiki):
    prompt = f"""
You are a geopolitical and financial prediction expert.

TASK: Predict one highly likely and impactful event that may happen TOMORROW related to the topic: "{topic}".

Base your answer only on verified data and current intelligence from:
- News: {news}
- Wikipedia: {wiki}

RULES:
- Start with a bold HEADLINE.
- Follow it with short structured reasoning in bullet or paragraph form.
- Mention real names (countries, companies, leaders).
- Avoid vague phrases (e.g., "may", "possibly", "could").
- If no significant forecast can be made with confidence, return exactly: "Nothing significant to predict for tomorrow."

Return only the forecast. No extra comments.
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
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        text = result["choices"][0]["message"]["content"].strip()
        return text
    except Exception as e:
        return f"Error generating prediction: {str(e)}"

# --- Prediction Update Logic ---
def update_predictions():
    global predictions_data
    predictions_data = []
    print(f"[{datetime.datetime.now()}] Updating predictions...")

    for topic in TOPICS:
        news = get_news_articles(topic)
        wiki = get_wikipedia_summary(topic)
        result = generate_prediction(topic, news, wiki)

        if "nothing significant" in result.lower():
            continue

        predictions_data.append({
            "topic": topic,
            "text": result,
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    print("Prediction update complete.")

# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html", predictions=predictions_data)

@app.route("/api/predictions")
def api_predictions():
    return jsonify(predictions_data)

# --- Scheduler ---
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_predictions, trigger="interval", hours=24)
scheduler.start()

# Initial Prediction Run
update_predictions()

# --- App Runner ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
