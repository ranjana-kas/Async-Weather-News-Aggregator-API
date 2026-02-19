import asyncio
import os
from typing import List, Dict
from dotenv import load_dotenv
from utils.http_client import AsyncClientWrapper

load_dotenv()  

API_KEY = os.getenv("GNEWS_API_KEY")

async def fetch_category(query: str, count: int) -> List[str]:
    client = AsyncClientWrapper.get_client()
    url = f"https://gnews.io/api/v4/search?q={query}&max={count}&lang=en&apikey={API_KEY}"
    
    try:
        response = await client.get(url, timeout=5.0)
        data = response.json()
        
        # DEBUGGING: Print the raw response to your terminal
        if response.status_code != 200:
            print(f" API ERROR for '{query}': {data}")  # <--- Look for this in your terminal!
            return []
            
        return [article["title"] for article in data.get("articles", [])]
        
    except Exception as e:
        print(f"⚠️ NETWORK ERROR for '{query}': {e}")  # <--- Or this!
        return []

# FIX: Add 'city: str' or 'query: str' here so it matches main.py
async def get_news(city: str) -> Dict[str, List[str]]:
    # We use the 'city' variable to make the news local to that area [cite: 60]
    results = await asyncio.gather(
        fetch_category(city, 5),          # 5 Local News [cite: 45]
        fetch_category("India", 3),       # 3 National News
        fetch_category("World", 2)        # 2 World News
    )
    
    return {
        "city_news": results[0],
        "national_news": results[1],
        "world_news": results[2]
    }