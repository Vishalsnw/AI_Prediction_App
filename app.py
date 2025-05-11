from flask import Flask, render_template, jsonify from openai import OpenAI import wikipedia import random import requests import feedparser from newspaper import Article import os from dotenv import load_dotenv from apscheduler.schedulers.background import BackgroundScheduler import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) app = Flask(name)

fields = [ "Politics", "Economy", "Health", "Technology", "Education", "Sports", "Weather", "Stock Market", "Entertainment", "Business", "War", "Fashion" ]

latest_predictions = {}

def get_news_articles(topic, max_articles=2): query = topic.replace(" ", "+") rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN" feed = feedparser.parse(rss_url) full_texts = "" count = 0 for entry in feed.entries: try: article = Article(entry.link) article.download() article.parse() full_texts += f"TITLE: {article.title}\n{article.text}\n\n" count += 1 except: continue if count >= max_articles: break return full_texts if full_texts else "No recent articles found."

def get_wikipedia_summary(topic): try: return wikipedia.summary(topic, sentences=5) except: return "No Wikipedia info available."

def get_astrology_insight(): choices = [ "Mars is pushing aggressive trends in this field.", "Saturn suggests delays or restructuring may come soon.", "Mercury retrograde may cause miscommunication or data issues.", "Lunar energy indicates public emotion and social tension.", "Jupiter brings expansion and long-term planning vibes." ] return random.choice(choices)

def generate_prediction(topic, context, wiki, astro): prompt = ( f"You are a professional forecaster. Based on the latest news, Wikipedia, and astrology, write a detailed 7–14 day prediction for the topic: {topic}.\n" f"Be specific. Mention concrete entities like companies, countries, politicians, or products.\n" f"Write like a professional analyst's post with paragraphs, reasoning, and potential developments.\n" f"\n[News]\n{context}\n\n[Wikipedia]\n{wiki}\n\n[Astrology]\n{astro}\n" ) try: response = client.chat.completions.create( model="gpt-3.5-turbo", messages=[ {"role": "system", "content": "You are an expert in global forecasting."}, {"role": "user", "content": prompt} ], temperature=0.7, max_tokens=800 ) return response.choices[0].message.content.strip() except Exception as e: return f"Error generating prediction: {e}"

def generate_all_predictions(): global latest_predictions new_predictions = {} for field in fields: news = get_news_articles(field) wiki = get_wikipedia_summary(field) astro = get_astrology_insight() prediction = generate_prediction(field, news, wiki, astro) new_predictions[field] = prediction latest_predictions = new_predictions print(f"Predictions updated: {datetime.datetime.now()}")

scheduler = BackgroundScheduler() scheduler.add_job(generate_all_predictions, 'interval', hours=24) scheduler.start()

Run once at startup

generate_all_predictions()

@app.route("/") def home(): return render_template("index.html", fields=fields)

@app.route("/predict/<topic>") def predict_topic(topic): if topic not in fields: return jsonify({"error": "Invalid topic"}), 400 prediction = latest_predictions.get(topic, "Prediction not available yet.") return jsonify({"prediction": prediction})

if name == "main": port = int(os.environ.get("PORT", 5000)) app.run(host="0.0.0.0", port=port)

