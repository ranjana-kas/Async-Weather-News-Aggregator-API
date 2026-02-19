from pydantic import BaseModel
from typing import List, Optional
from schemas.weather import WeatherResponse 

class NewsResponse(BaseModel):
    city_news: List[str]
    national_news: List[str]
    world_news: List[str]

class DailyBriefing(BaseModel):
    weather: Optional[WeatherResponse] = None
    news: NewsResponse # This now contains all three categories
    warning: Optional[str] = None 
    execution_time: float = 0.0