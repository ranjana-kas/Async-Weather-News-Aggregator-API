from pydantic import BaseModel
from typing import List, Optional
# ADD THIS IMPORT BELOW
from schemas.weather import WeatherResponse 

class NewsResponse(BaseModel):
    headlines: List[str]

class DailyBriefing(BaseModel):
    # Now WeatherResponse is recognized!
    weather: Optional[WeatherResponse] = None
    news: List[str] = []
    warning: Optional[str] = None