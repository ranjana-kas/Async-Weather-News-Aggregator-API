#----- Throttle API calls to 100 per day -----#
import json
import os
from datetime import datetime

QUOTA_FILE = "quota.json"
DAILY_LIMIT = 100

def check_and_increment_quota() -> bool:
    """
    Returns True if we have credit left.
    Returns False if we hit the limit.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Load existing data
    if os.path.exists(QUOTA_FILE):
        with open(QUOTA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"date": today, "count": 0}

    # 2. Reset counter if it's a new day
    if data["date"] != today:
        data = {"date": today, "count": 0}

    # 3. Check Limit
    if data["count"] >= DAILY_LIMIT:
        return False
    
    # 4. Increment and Save
    data["count"] += 1
    with open(QUOTA_FILE, "w") as f:
        json.dump(data, f)
        
    return True