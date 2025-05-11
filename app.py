import os
from flask import Flask, request, jsonify
from openai import OpenAI
import wikipedia
import random
import feedparser
from newspaper import Article

app = Flask(__name__)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def get_google_news_articles(topic, max_articles=3):
    query = topic.replace(" ", "+")
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN"
    feed = feedparser.parse(rss_url)

    full_texts = ""
    count = 0

    for entry in feed.entries:
        url = entry.link
        try:
            article = Article(url)
            article.download()
            article.parse()
            full_texts += f"TITLE: {article.title}\n{article.text}\n\n"
            count += 1
        except:
            continue
        if count >= max_articles:
            break

    return full_texts if full_texts else "No full articles found."

def get_wikipedia_info(topic):
    try:
        summary = wikipedia.summary(topic, sentences=5)
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            summary = wikipedia.summary(e.options[0], sentences=5)
        except:
            summary = "No clear Wikipedia summary available."
    except wikipedia.exceptions.PageError:
        results = wikipedia.search(topic)
        if results:
            try:
                summary = wikipedia.summary(results[0], sentences=5)
            except:
                summary = "No Wikipedia summary found."
        else:
            summary = "No Wikipedia page found."
    return summary

def get_astrology_insight():
    templates = [
        "Mars influence indicates a period of aggressive decision-making and bold innovation.",
        "Saturn alignment may trigger delays in execution and increased regulatory scrutiny.",
        "Mercury retrograde could affect communications and tech stability temporarily.",
        "Lunar phases suggest rising public sentiment and emotional engagement with the topic.",
        "Jupiter’s position supports expansion and policy reforms during this cycle."
    ]
    return random.choice(templates)

def generate_prediction(topic, context, wiki_info, astrology):
    prompt = (
        f"You are an expert analyst combining current news, historical context, and astrological patterns "
        f"to forecast likely events related to the following topic.\n\n"
        f"Topic: {topic}\n\n"
        f"[News Context]\n{context}\n\n"
        f"[Wikipedia Summary]\n{wiki_info}\n\n"
        f"[Astrological Insight]\n{astrology}\n\n"
        f"Using this information, provide a specific and realistic prediction for the next 7 to 21 days. "
        f"Include likely developments, concrete actions by involved parties, possible outcomes, and any critical timing. "
        f"Do not use vague language like 'stay alert' or 'be careful'. Make it sound like a real forecast.\n\n"
        f"Your answer should include:\n"
        f"- 1-2 short-term developments that may occur\n"
        f"- Specific challenges and decisions\n"
        f"- A likely overall outcome\n\n"
        f"Write in a clear, confident, and analytical tone:"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional foresight analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.75,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    topic = data.get("topic", "")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    context = get_google_news_articles(topic)
    wiki_info = get_wikipedia_info(topic)
    astrology = get_astrology_insight()
    prediction = generate_prediction(topic, context, wiki_info, astrology)

    return jsonify({"prediction": prediction})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
