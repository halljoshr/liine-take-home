"""
This is a simple FastAPI application that returns a list of restaurants that are open at a given time.

The application is designed to be used as a RESTful API.

--Josh

"""

from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime, time
from pydantic import BaseModel
from typing import List
import uvicorn
import logging
import json
from sqlalchemy.orm import Session
from database import get_db, RestaurantHours

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()


# Did this with a pydantic model but have done something similar with a dataclass as well.
class RestaurantResponse(BaseModel):
    restaurant_names: List[str]


def is_time_between(current_time: time, start_time: time, end_time: time) -> bool:
    """
    Check if current_time is between start_time and end_time, handling overnight hours.

    Args:
        current_time (time): The time to check
        start_time (time): The opening time
        end_time (time): The closing time

    Returns:
        bool: True if current_time is between start_time and end_time
    """
    if start_time <= end_time:
        # Normal case: start_time is before end_time (e.g., 09:00 to 17:00)
        return start_time <= current_time <= end_time
    else:
        # Overnight case: start_time is after end_time (e.g., 23:00 to 01:00)
        return current_time >= start_time or current_time <= end_time


@app.get("/restaurants", response_model=RestaurantResponse)
def get_restaurants(
    datetime_str: str, db: Session = Depends(get_db)
) -> RestaurantResponse:
    """
    Get the list of restaurants that are open at a given time.

    Args:
        datetime_str (str): The datetime string in the format YYYY-MM-DD HH:MM:SS
        db (Session): Database session

    Returns:
        RestaurantResponse: A response containing a list of restaurant names that are open at the given time.

    Todo:
        - Handle restaurant not found
        - Add error handling
        - Add tests
    """
    try:
        # Parse the input datetime string
        query_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        day_of_week = query_time.weekday()
        current_time = query_time.time()

        logger.debug(f"Parsed datetime: {query_time}")
        logger.debug(f"Day of week (0=Monday): {day_of_week}")
        logger.debug(f"Current time: {current_time}")

        # Query restaurants from database
        restaurants = (
            db.query(RestaurantHours)
            .filter(RestaurantHours.day_of_week == day_of_week)
            .all()
        )

        # Filter restaurants that are open at the current time
        open_restaurants = [
            r.restaurant_name
            for r in restaurants
            if is_time_between(current_time, r.open_time, r.close_time)
        ]

        # Remove duplicates while preserving order
        restaurant_names = list(dict.fromkeys(open_restaurants))

        logger.debug(f"Found {len(restaurant_names)} restaurants open at this time")
        logger.debug("Open restaurants:\n" + json.dumps(restaurant_names, indent=2))

        return RestaurantResponse(restaurant_names=restaurant_names)

    except ValueError:
        logger.error(f"Invalid datetime format received: {datetime_str}")
        raise HTTPException(
            status_code=400,
            detail="Invalid datetime format. Please use YYYY-MM-DD HH:MM:SS format",
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5555)
