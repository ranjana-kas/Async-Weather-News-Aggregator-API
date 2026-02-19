from utils.http_client import AsyncClientWrapper
from schemas.weather import WeatherResponse
from fastapi import HTTPException

async def get_coords(city: str):
    """Turns a city name into Latitude and Longitude."""
    client = AsyncClientWrapper.get_client()
    
    # Using Open-Meteo's free geocoding service
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    response = await client.get(url)
    data = response.json()
    
    if not data.get("results"):
        return None
    
    result = data["results"][0]
    return {"lat": result["latitude"], "lon": result["longitude"], "name": result["name"]}

async def get_weather(city: str) -> WeatherResponse:
    coords = await get_coords(city) 
    if not coords:
        raise HTTPException(status_code=404, detail="City not found")
    
    client = AsyncClientWrapper.get_client()
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
    
    response = await client.get(url)
    data = response.json()["current_weather"]
    
    condition_map = {0: "Sunny", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast", 45: "Foggy", 51: "Drizzle", 61: "Rainy"}
    condition_text = condition_map.get(data["weathercode"], "Cloudy")

    return WeatherResponse(
        city=coords["name"],
        temperature=data["temperature"],
        condition=condition_text 
    )

