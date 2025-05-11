background_job.py

import requests

BASE_URL = "https://your-app-name.onrender.com"  # Replace with your actual Render app URL fields = [ "Politics", "Economy", "Health", "Technology", "Education", "Sports", "Weather", "Stock Market", "Entertainment", "Business", "War", "Fashion" ]

def run_daily_predictions(): for topic in fields: url = f"{BASE_URL}/predict/{topic.replace(' ', '%20')}" try: response = requests.get(url, timeout=60) if response.status_code == 200: print(f"Prediction for {topic}: Success") else: print(f"Prediction for {topic} failed: {response.status_code}") except Exception as e: print(f"Error for {topic}: {e}")

if name == "main": run_daily_predictions()

