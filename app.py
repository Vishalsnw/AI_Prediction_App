from flask import Flask, render_template, jsonify
from openai import OpenAI
import wikipedia
import random
import requests
import feedparser
from newspaper import Article
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = Flask(__name__)

fields = [
    "Politics", "Economy", "Health", "Technology", "Education", "Sports",
    "Weather", "Stock Market", "Entertainment", "Business", "War", "Fashion"
]

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
    return random.choice([
        "Mars may bring aggressive movement in this sector.",
        "Saturn signals possible restructuring or delays.",
        "Mercury retrograde could create confusion in data or decisions.",
        "Lunar energy reflects heightened public emotion.",
        "Jupiter supports expansion, growth, and bold moves."
    ])

def generate_prediction(topic, news, wiki, astro):
    prompt = (
        f"You are a sharp professional forecaster. Analyze recent events and forecast what could happen in the next 7–14 days.\n"
        f"Focus: {topic}\n\n[News Data]\n{news}\n\n[Wikipedia]\n{wiki}\n\n[Astrological Insight]\n{astro}\n\n"
        "Write the prediction in a clear, structured, professional tone. Mention specific people, companies, countries, or trends involved. "
        "Organize your response like a short article or post with paragraphs, not a list. Avoid vague or generic advice."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert prediction analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

@app.route("/")
def home():
    return render_template("index.html", fields=fields)

@app.route("/predict/<topic>")
def predict_topic(topic):
    if topic not in fields:
        return jsonify({"error": "Invalid topic"}), 400
    news = get_news_articles(topic)
    wiki = get_wikipedia_summary(topic)
    astro = get_astrology_insight()
    prediction = generate_prediction(topic, news, wiki, astro)
    return jsonify({"prediction": prediction})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
