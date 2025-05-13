from flask import Flask, render_template, jsonify
from openai import OpenAI
import feedparser
from newspaper import Article
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import random

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = Flask(__name__)

# Store daily prediction
todays_prediction = ""

# Grab latest headlines and content
def get_combined_news(max_articles=5):
    topics = ["politics", "technology", "economy", "business", "geopolitics", "health", "science", "sports", "environment", "conflict", "natural disaster"]
    all_text = ""
    random.shuffle(topics)
    for topic in topics:
        feed_url = f"https://news.google.com/rss/search?q={topic}&hl=en-IN&gl=IN"
        feed = feedparser.parse(feed_url)
        count = 0
        for entry in feed.entries:
            try:
                article = Article(entry.link)
                article.download()
                article.parse()
                all_text += f"TITLE: {article.title}\n{article.text}\n\n"
                count += 1
                if count >= max_articles:
                    break
            except:
                continue
    return all_text or "No recent articles found."

def get_astrology_hint():
    hints = [
        "Mars is triggering aggression and volatility tomorrow.",
        "Mercury retrograde may cause shocking communication errors.",
        "Jupiter's influence may lead to expansion or unexpected announcements.",
        "Saturn indicates restrictions or a major government move.",
        "A lunar phase tomorrow may drive emotional or public reactions."
    ]
    return random.choice(hints)

def generate_tomorrow_prediction(news, astrology):
    prompt = (
        "You are a world-class analyst and forecaster. Based on the following real news and astrological energy, "
        "predict one or more **bold and sensational** events that may realistically happen **tomorrow** (not next week). "
        "Mention real names — people, countries, companies, places, politicians, or products. If nothing significant is predictable, just say: 'Nothing significant to predict for tomorrow.'\n\n"
        f"[News]\n{news}\n\n"
        f"[Astrology]\n{astrology}\n\n"
        "Output must be structured like a news-style forecast post. Write clearly in paragraphs, avoid generic advice, and focus only on bold, specific, likely events for tomorrow."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a forecasting AI that only makes bold, specific predictions for the next day."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        content = response.choices[0].message.content.strip()
        return content
    except Exception as e:
        return f"Error: {e}"

def update_prediction():
    global todays_prediction
    print(f"[{datetime.datetime.now()}] Updating tomorrow's prediction...")
    news = get_combined_news()
    astrology = get_astrology_hint()
    prediction = generate_tomorrow_prediction(news, astrology)
    if "Nothing significant" in prediction:
        todays_prediction = "Nothing significant to predict for tomorrow."
    else:
        todays_prediction = prediction
    print("Prediction updated.")

# Schedule update daily
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_prediction, trigger="interval", hours=24)
scheduler.start()

# Run once on startup
update_prediction()

@app.route("/")
def home():
    return render_template("index.html", prediction=todays_prediction)

@app.route("/predict")
def get_prediction():
    return jsonify({"prediction": todays_prediction})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
