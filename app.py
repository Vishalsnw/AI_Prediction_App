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

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = Flask(__name__)

fields = [
    "Politics", "Economy", "Health", "Technology", "Education", "Sports",
    "Weather", "Stock Market", "Entertainment", "Business", "War", "Fashion"
]

predictions_data = {}

def get_news_articles(topic, max_articles=2):
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
        return wikipedia.summary(topic, sentences=5)
    except:
        return "No Wikipedia info available."

def get_astrology_insight():
    choices = [
        "Mars is pushing aggressive trends in this field.",
        "Saturn suggests delays or restructuring may come soon.",
        "Mercury retrograde may cause miscommunication or data issues.",
        "Lunar energy indicates public emotion and social tension.",
        "Jupiter brings expansion and long-term planning vibes."
    ]
    return random.choice(choices)

def generate_prediction(topic, context, wiki, astro):
    prompt = (
        f"You are a professional global analyst. Based on the latest news, Wikipedia insights, and astrology, "
        f"predict **what is most likely to happen tomorrow** in the field of {topic}.\n\n"
        f"Include specific names (e.g., people, companies, countries, products, politicians) and detailed references.\n\n"
        f"Structure the response into clear, concise **paragraphs** and use a professional tone.\n\n"
        f"[News Content]\n{context}\n\n"
        f"[Wikipedia Summary]\n{wiki}\n\n"
        f"[Astrology]\n{astro}\n\n"
        f"Forecast format:\n- Title: [Short title of the forecast]\n- Date: [Tomorrow's Date]\n- Paragraphs: Clearly formatted, insightful analysis with names and expected developments."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional forecaster who writes detailed daily predictions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating prediction: {e}"

def update_all_predictions():
    global predictions_data
    print(f"[{datetime.datetime.now()}] Updating all predictions...")
    predictions_data = {}
    for field in fields:
        news = get_news_articles(field)
        wiki = get_wikipedia_summary(field)
        astro = get_astrology_insight()
        prediction = generate_prediction(field, news, wiki, astro)
        predictions_data[field] = prediction
    print("All predictions updated.")

@app.route("/")
def home():
    return render_template("index.html", fields=fields)

@app.route("/predict/<topic>")
def predict_topic(topic):
    if topic not in predictions_data:
        return jsonify({"error": "Prediction not available"}), 404
    return jsonify({"prediction": predictions_data[topic]})

# Schedule daily updates
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_all_predictions, trigger="interval", hours=24)
scheduler.start()

# Initial load
update_all_predictions()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
