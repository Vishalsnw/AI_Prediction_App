from flask import Flask, render_template, jsonify from openai import OpenAI import wikipedia import random import requests import feedparser from newspaper import Article import os from dotenv import load_dotenv from apscheduler.schedulers.background import BackgroundScheduler import datetime import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) app = Flask(name)

fields = [ "Politics", "Economy", "Health", "Technology", "Education", "Sports", "Weather", "Stock Market", "Entertainment", "Business", "War", "Fashion" ]

PREDICTIONS_FILE = "predictions.json"

def get_news_articles(topic, max_articles=2): query = topic.replace(" ", "+") rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN" feed = feedparser.parse(rss_url) full_texts = "" count = 0 for entry in feed.entries: try: article = Article(entry.link) article.download() article.parse() full_texts += f"TITLE: {article.title}\n{article.text}\n\n" count += 1 except: continue if count >= max_articles: break return full_texts if full_texts else "No recent articles found."

def get_wikipedia_summary(topic): try: return wikipedia.summary(topic, sentences=5) except: return "No Wikipedia info available."

def get_astrology_insight(): choices = [ "Mars is pushing aggressive trends in this field.", "Saturn suggests delays or restructuring may come soon.", "Mercury retrograde may cause miscommunication or data issues.", "Lunar energy indicates public emotion and social tension.", "Jupiter brings expansion and long-term planning vibes." ] return random.choice(choices)

def generate_prediction(topic, context, wiki, astro): prompt = ( f"You're a smart analyst. Based on recent news, historical info, and astrology, predict what will happen in the next 7–14 days." f" Field: {topic}\n\n[News]\n{context}\n\n[Wiki]\n{wiki}\n\n[Astro]\n{astro}\n\n" f"Write a professional, specific, paragraph-based forecast using real names (companies, politicians, countries, products, etc). Avoid vague advice." ) try: response = client.chat.completions.create( model="gpt-3.5-turbo", messages=[ {"role": "system", "content": "You are an expert geopolitical and market analyst."}, {"role": "user", "content": prompt} ], temperature=0.7, max_tokens=600 ) return response.choices[0].message.content.strip() except Exception as e: return f"Error generating prediction: {e}"

def update_predictions(): all_predictions = {} for field in fields: news = get_news_articles(field) wiki = get_wikipedia_summary(field) astro = get_astrology_insight() prediction = generate_prediction(field, news, wiki, astro) all_predictions[field] = { "text": prediction, "timestamp": datetime.datetime.utcnow().isoformat() } with open(PREDICTIONS_FILE, "w") as f: json.dump(all_predictions, f)

@app.route("/") def home(): return render_template("index.html", fields=fields)

@app.route("/predict/<topic>") def predict_topic(topic): if topic not in fields: return jsonify({"error": "Invalid topic"}), 400 try: with open(PREDICTIONS_FILE, "r") as f: predictions = json.load(f) if topic in predictions: return jsonify({"prediction": predictions[topic]["text"]}) except: pass return jsonify({"error": "Prediction not found."})

if name == "main": scheduler = BackgroundScheduler() scheduler.add_job(update_predictions, "interval", hours=24) scheduler.start() update_predictions()  # Initial call

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

