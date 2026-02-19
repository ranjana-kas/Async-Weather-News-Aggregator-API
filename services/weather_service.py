from utils.http_client import AsyncClientWrapper
from schemas.weather import WeatherResponse
from fastapi import HTTPException

# Simple mapping for demonstration
CITY_COORDS = {
    "delhi": {"lat": 28.61, "lon": 77.20},
    "bilaspur": {"lat": 22.07, "lon": 82.13},
    "london": {"lat": 51.50, "lon": -0.12}
}

async def get_weather(city: str) -> WeatherResponse:
    city_lower = city.lower()
    if city_lower not in CITY_COORDS:
        raise HTTPException(status_code=404, detail="City not supported") [cite: 38, 91]

    coords = CITY_COORDS[city_lower]
    client = AsyncClientWrapper.get_client()
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
        response = await client.get(url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Weather API Error") [cite: 39]
            
        data = response.json()["current_weather"]
        return WeatherResponse(
            city=city.capitalize(),
            temperature=data["temperature"],
            condition=str(data["weathercode"]) # Codes can be mapped to strings later
        )
    except Exception:
        raise HTTPException(status_code=504, detail="Weather API Timeout") [cite: 40, 90]