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
                    "You are a prophetic AI inspired by Nostradamus, Baba Vanga, and psychic visionaries. "
                    "You study signs from news, history, symbols, energy, and sacred books. Predict with mystical clarity."
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
Search the Earth, skies, and signals. Observe where tomorrow's fate is shifting.

Return ONE topic (3 to 6 words) where powerful energy is gathering.

Example format: "Oil conflict Iran", "US-China cyber tension"
"""
    return deepseek_generate(prompt).strip()

def get_news_headlines(topic):
    try:
        rss_url = f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}&hl=en-IN&gl=IN"
        feed = feedparser.parse(rss_url)
        headlines = "\n".join([entry.title for entry in feed.entries[:5]])
        return headlines or "No recent headlines."
    except:
        return "No recent headlines."

def get_wikipedia_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=2)
    except:
        return "No Wikipedia summary available."

def generate_prediction():
    topic = find_best_topic()
    news = get_news_headlines(topic)
    wiki = get_wikipedia_summary(topic)

    prompt = f"""
Topic of Interest: "{topic}"

News Headlines:
{news}

Wikipedia Info:
{wiki}

TASK: Based on ancient prophecy wisdom and current signs, predict ONE major event that may happen TOMORROW.

Give result like:
**HEADLINE:** Short, powerful line
**Why:** In simple language
**Who is affected:** Real names/places
**Timing:** Why it will happen tomorrow
If nothing major seen, just say: "No signs for tomorrow."
"""
    prediction = deepseek_generate(prompt)

    if "no signs" in prediction.lower():
        return []

    return [{
        "title": topic,
        "text": prediction.strip(),
        "confidence": 91
    }]

@app.route("/")
def home():
    predictions = generate_prediction()
    return render_template("index.html", predictions=predictions)

@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})
