from flask import Flask, render_template import os import wikipedia import random import feedparser from newspaper import Article from openai import OpenAI from datetime import datetime

app = Flask(name) client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOPICS = [ "politics", "sports", "health", "economy", "technology", "weather", "education", "business", "fashion", "entertainment", "stock market" ]

def get_news_articles(topic, max_articles=2): query = topic.replace(" ", "+") rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN" feed = feedparser.parse(rss_url)

text = ""
count = 0
for entry in feed.entries:
    try:
        article = Article(entry.link)
        article.download()
        article.parse()
        text += f"TITLE: {article.title}\n{article.text}\n\n"
        count += 1
    except:
        continue
    if count >= max_articles:
        break
return text if text else "No news found."

def get_wikipedia_info(topic): try: return wikipedia.summary(topic, sentences=3) except: return "Wikipedia data not found."

def get_astrology(): return random.choice([ "Mars influence suggests assertive events.", "Mercury retrograde may affect communication.", "Saturn might bring delays or discipline.", "Jupiter's alignment may expand impact.", "Lunar energy enhances emotions in decisions." ])

def generate_prediction(topic, context, wiki, astro): prompt = f""" Analyze and predict events for the topic: {topic}. [News]\n{context} [Wikipedia]\n{wiki} [Astrology]\n{astro} Provide a clear, specific forecast for the next 7-21 days with: - Short-term developments - Decisions or challenges - Probable outcomes """ try: response = client.chat.completions.create( model="gpt-3.5-turbo", messages=[ {"role": "system", "content": "You are an expert prediction analyst."}, {"role": "user", "content": prompt} ], temperature=0.7, max_tokens=500 ) return response.choices[0].message.content.strip() except Exception as e: return f"Error generating prediction: {str(e)}"

@app.route("/") def index(): predictions = [] for topic in TOPICS: news = get_news_articles(topic) wiki = get_wikipedia_info(topic) astro = get_astrology() prediction = generate_prediction(topic, news, wiki, astro) predictions.append({"topic": topic.title(), "prediction": prediction})

today = datetime.now().strftime("%B %d, %Y")
return render_template("index.html", predictions=predictions, date=today)

if name == "main": app.run(host="0.0.0.0", port=10000)

