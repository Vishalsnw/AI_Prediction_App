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
            {"role": "system", "content": "You are a super-intelligent forecasting AI that finds and predicts important events."},
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
Think like an expert journalist, military strategist, and financial analyst combined.

TASK: Analyze global trends and identify ONE topic that may have a HIGH IMPACT TOMORROW.

Only return the topic in 5 words or less. No extra explanation.
"""
    return deepseek_generate(prompt).strip()

def get_news_headlines(topic):
    try:
        rss_url = f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}&hl=en-IN&gl=IN"
        feed = feedparser.parse(rss_url)
        headlines = "\n".join([entry.title for entry in feed.entries[:5]])
        return headlines if headlines else "No recent headlines."
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
Topic selected: "{topic}"

Sources:
- News: {news}
- Wikipedia: {wiki}

TASK: Predict if something impactful may happen TOMORROW regarding this topic.

If yes, provide:
- A bold HEADLINE
- Clear logic and justification
- Mention real names/places/companies

If not, say: "Nothing significant to predict for tomorrow."
"""
    prediction = deepseek_generate(prompt)

    if "nothing significant" not in prediction.lower():
        return [{
            "title": topic,
            "text": prediction,
            "confidence": 90,
            "accuracy": 90
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
