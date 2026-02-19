import os
from typing import List
from dotenv import load_dotenv
from utils.http_client import AsyncClientWrapper
from fastapi import HTTPException

load_dotenv()
API_KEY = os.getenv("GNEWS_API_KEY")

async def get_news() -> List[str]:
    client = AsyncClientWrapper.get_client()
    url = f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&country=us&max=5&apikey={API_KEY}"
    
    try:
        response = await client.get(url, timeout=5.0)
        if response.status_code != 200:
            # If the API fails, return a 502 Bad Gateway [cite: 54]
            raise HTTPException(status_code=502, detail="News API unreachable")
        
        data = response.json()
        # Extract only the 'title' from each article [cite: 49-51]
        headlines = [article["title"] for article in data.get("articles", [])]
        return headlines
    except Exception:
        # Handle timeouts [cite: 55]
        raise HTTPException(status_code=504, detail="News API timed out")