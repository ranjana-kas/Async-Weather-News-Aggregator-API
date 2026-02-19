import asyncio
import os
from typing import List, Dict
from dotenv import load_dotenv
from utils.http_client import AsyncClientWrapper
from utils.quota_manager import check_and_increment_quota

load_dotenv()  

API_KEY = os.getenv("GNEWS_API_KEY")

async def fetch_category(query: str, count: int) -> List[str]:

    if not check_and_increment_quota():
        print("⚠️ DAILY QUOTA EXCEEDED: Skipping GNews call.")
        return ["(System: Daily News Quota Exceeded. Please try again tomorrow.)"]

    client = AsyncClientWrapper.get_client()
    url = f"https://gnews.io/api/v4/search?q={query}&max={count}&lang=en&apikey={API_KEY}"
    
    try:
        response = await client.get(url, timeout=5.0)
        data = response.json()
        
        if response.status_code != 200:
            print(f" API ERROR for '{query}': {data}")  
            return []
            
        return [article["title"] for article in data.get("articles", [])]
        
    except Exception as e:
        print(f"⚠️ NETWORK ERROR for '{query}': {e}")  
        return []


async def get_news(city: str) -> Dict[str, List[str]]:
   
    results = await asyncio.gather(
        fetch_category(city, 5),          # 5 Local News 
        fetch_category("India", 3),       # 3 National News
        fetch_category("World", 2)        # 2 World News
    )
    
    return {
        "city_news": results[0],
        "national_news": results[1],
        "world_news": results[2]
    }