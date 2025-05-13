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
import urllib.parse

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

prediction_data = {"content": "Loading prediction..."}

# Secret Intelligence Simulation
INTELLIGENCE_MODES = [
    "AI Secret Agent Mode",
    "Insider Leak Scan",
    "Global Digital Pulse",
    "Astro-War Alert",
    "Deep Persona (Whistleblower)"
]

def get_news_articles(query, max_articles=2):
    query_encoded = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=en-IN&gl=IN"
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
    return full_texts or "No recent news found."

def get_wikipedia_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=4)
    except:
        return "No Wikipedia data found."

def get_astrology_insight():
    choices = [
        "Mars square Pluto indicates extreme tension or violent shifts.",
        "Mercury retrograde may trigger miscommunication in leadership.",
        "Lunar eclipse aligned with Uranus shows unpredictable public backlash.",
        "Saturn in Pisces hints institutional secrets may leak.",
        "Venus combust under Scorpio warns of scandals in finance or media."
    ]
    return random.choice(choices)

def generate_prediction(context, wiki, astro):
    prompt = (
        "You are an elite AI analyst with access to secret intelligence, insider business leaks, trending social signals, and astrological patterns. "
        "Based on all this, predict one sensational, realistic event that might happen TOMORROW. "
        "Mention real names (politicians, countries, companies, products, regions). Be bold and structured. If no strong signal is found, say 'Nothing significant to predict for tomorrow.'\n\n"
        f"[News Signals]\n{context}\n\n"
        f"[Wikipedia Insight]\n{wiki}\n\n"
        f"[Astrological Interpretation]\n{astro}\n\n"
        "Your forecast must feel shocking yet plausible — written like a high-level intel leak or special ops briefing."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an elite secret analyst AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating prediction: {e}"

def scan_and_generate_prediction():
    print(f"[{datetime.datetime.now()}] Scanning intelligence sources...")

    hot_topics = ["Elon Musk", "Ukraine", "Stock Market", "Apple", "Taiwan", "Cryptocurrency", "Israel", "Oil prices", "NATO", "Xi Jinping"]
    selected_topic = random.choice(hot_topics)

    print(f"Selected dynamic topic: {selected_topic}")
    news = get_news_articles(selected_topic)
    wiki = get_wikipedia_summary(selected_topic)
    astro = get_astrology_insight()
    prediction = generate_prediction(news, wiki, astro)

    global prediction_data
    prediction_data["content"] = prediction

@app.route("/")
def home():
    return render_template("index.html", prediction=prediction_data["content"])

@app.route("/predict")
def predict():
    return jsonify(prediction_data)

# Schedule daily prediction
scheduler = BackgroundScheduler()
scheduler.add_job(func=scan_and_generate_prediction, trigger="interval", hours=24)
scheduler.start()

# First-time prediction
scan_and_generate_prediction()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
