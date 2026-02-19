import asyncio
import time
import os
from fastapi import FastAPI, HTTPException, Request, status, BackgroundTasks
from typing import Dict

# Import your services and schemas
from services.weather_service import get_weather
from services.news_service import get_news
from schemas.news import DailyBriefing, NewsResponse
from utils.http_client import AsyncClientWrapper

# --- 1. INITIALIZE APP FIRST ---
app = FastAPI(title="Async Aggregator API")

# --- 2. GLOBAL STORES (Stretch Goals) ---
WEATHER_CACHE: Dict[str, dict] = {}  
REQUEST_COUNTS: Dict[str, list] = {}  

# --- 3. LIFESPAN EVENTS ---
@app.on_event("startup")
async def startup_event():
    AsyncClientWrapper.get_client()

@app.on_event("shutdown")
async def shutdown_event():
    await AsyncClientWrapper.close_client()

# --- 4. MIDDLEWARE (Rate Limiting)  ---
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    
    if client_ip not in REQUEST_COUNTS:
        REQUEST_COUNTS[client_ip] = []
    
    # Keep only requests from the last 60 seconds
    REQUEST_COUNTS[client_ip] = [t for t in REQUEST_COUNTS[client_ip] if now - t < 60]
    
    if len(REQUEST_COUNTS[client_ip]) >= 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="Rate limit: 10 requests per minute"
        )
    
    REQUEST_COUNTS[client_ip].append(now)
    return await call_next(request)

# --- 5. BACKGROUND TASKS  ---
def log_request_to_file(city: str, status_code: int):
    with open("api_logs.txt", "a") as f:
        f.write(f"City: {city} | Status: {status_code} | Time: {time.ctime()}\n")

# --- 6. ENDPOINTS ---

@app.get("/weather/{city}", response_model=None)
async def weather_endpoint(city: str):
    # Caching Stretch Goal 
    if city.lower() in WEATHER_CACHE:
        cache_data, timestamp = WEATHER_CACHE[city.lower()]
        if time.time() - timestamp < 600:  # 10 minutes cache 
            return cache_data
            
    data = await get_weather(city)
    WEATHER_CACHE[city.lower()] = (data, time.time())
    return data

@app.get("/news", response_model=NewsResponse)
async def news_endpoint():
    headlines = await get_news()
    return NewsResponse(headlines=headlines)

# ... existing imports ...

@app.get("/briefing/{city}", response_model=DailyBriefing)
async def briefing_endpoint(city: str, background_tasks: BackgroundTasks):
    start_time = time.perf_counter()
    results = await asyncio.gather(
        get_weather(city), 
        get_news(city=city), # News is now about the city!
        return_exceptions=True
    )
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    weather_res = results[0] if not isinstance(results[0], Exception) else None
    news_res = results[1] if not isinstance(results[1], Exception) else []
    
    warning = None
    if any(isinstance(r, Exception) for r in results):
        warning = "Partial data: One or more services failed."

    # Log to file in the background 
    background_tasks.add_task(log_request_to_file, city, 200)

    return DailyBriefing(
        weather=weather_res, 
        news=news_res, 
        warning=warning,
        execution_time=round(duration, 4) # Round to 4 decimal places
    )