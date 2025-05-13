from flask import Flask, render_template, jsonify
from openai import OpenAI
import wikipedia
import random
import requests
import feedparser
from newspaper import Article
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import json
import re

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = Flask(__name__)

predictions_data = []

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

def generate_prediction(topic, context, wiki):
    prompt = f"""
You are an elite global forecaster with access to insider intelligence, news scans, forums, and astrology.

Your task: Predict one shocking or significant event that may happen TOMORROW. Mention specific names: companies, politicians, countries, or regions.

Sources:
- News Articles: {context}
- Wikipedia Summary: {wiki}
- Astrology Insight: {random.choice(["Mars transit causing tension", "Mercury retrograde may cause disruption", "Saturn influence on economic shifts"])}

Rules:
1. Predict ONLY if confident. Else respond: "Nothing significant to predict for tomorrow."
2. Format professionally, like a headline + structured paragraphs.
3. Use bold statements, thrilling tone, real names.

Now, generate a bold, headline-worthy forecast.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a global intelligence forecaster AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating prediction: {e}"

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

# Daily background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_predictions, trigger="interval", hours=24)
scheduler.start()

# Initial prediction run
update_predictions()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
