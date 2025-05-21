"""
This script is used to transform the restaurant hours data from a CSV file to a more usable format.

--Josh
"""

import pandas as pd
import re
from datetime import datetime


# Function to parse time string to standardized format
def parse_time(time_str: str) -> str | None:
    """
    This function parses a time string to a standardized format.

    Args:
        time_str (str): A string containing a time

    Returns:
        str: A string containing the time in the format HH:MM:SS
    """

    time_str = time_str.strip().lower()
    # Handle formats like "11:00 am", "11 am", etc.
    if ":" in time_str:
        time_format = "%I:%M %p"
    else:
        time_format = "%I %p"

    # Special handling for 12 am/pm
    if time_str == "12 am":
        return "00:00:00"
    elif time_str == "12 pm":
        return "12:00:00"

    try:
        parsed_time = datetime.strptime(time_str, time_format)
        return parsed_time.strftime("%H:%M:%S")
    except ValueError:
        return None


# Function to expand day ranges
def expand_day_range(day_range: str) -> list:
    """
    This function expands a day range to a list of days.

    Args:
        day_range (str): A string containing a day range

    Returns:
        list: A list of days
    """

    day_map = {
        "mon": 0,
        "monday": 0,
        "tues": 1,
        "tuesday": 1,
        "wed": 2,
        "wednesday": 2,
        "thu": 3,
        "thurs": 3,  # did not see this in dataset but possible...
        "thursday": 3,
        "fri": 4,
        "friday": 4,
        "sat": 5,
        "saturday": 5,
        "sun": 6,
        "sunday": 6,
    }
    days = []

    # Handle ranges like "Mon-Fri"
    if "-" in day_range:
        start_day, end_day = day_range.lower().split("-")
        start_idx = day_map.get(start_day, 0)
        end_idx = day_map.get(end_day, 6)

        # Handle wrap-around if needed (e.g., Fri-Mon)
        # Do not think this is in the dataset but just in case
        if end_idx >= start_idx:
            days = list(range(start_idx, end_idx + 1))
        else:
            days = list(range(start_idx, 7)) + list(range(0, end_idx + 1))
    else:
        day_idx = day_map.get(day_range.lower(), None)
        if day_idx is not None:
            days = [day_idx]

    return days


# Main processing function
def transform_hours_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function transforms the restaurant hours data from a CSV file to a more usable format.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing the restaurant hours data

    Returns:
        pd.DataFrame: A pandas DataFrame with the restaurant hours data in the new format
    """
    result = []

    for _, row in df.iterrows():
        restaurant_name = row["Restaurant Name"]
        hours_text = row["Hours"]

        # Split by "/" which separates different day patterns
        day_patterns = hours_text.split("/")

        for pattern in day_patterns:
            pattern = pattern.strip()

            # Find where time starts by looking for patterns like "11 am", or "5 pm"
            # \d+ is one or more digits
            # (?::\d+)? is an optional colon followed by one or more digits
            # \s* is zero or more whitespace characters
            # (?:am|pm) is either "am" or "pm"
            time_match = re.search(r"\d+(?::\d+)?\s*(?:am|pm)", pattern, re.IGNORECASE)
            if not time_match:
                continue

            time_start_idx = time_match.start()
            day_part = pattern[:time_start_idx].strip()
            time_part = pattern[time_start_idx:].strip()

            # Parse the day ranges
            day_ranges = [d.strip() for d in day_part.split(",")]
            days = []
            for day_range in day_ranges:
                days.extend(expand_day_range(day_range))

            # Extract opening and closing times
            # The non-greedy ? in the first group is important because it ensures we don't accidentally capture too much.
            # I looked up the best regex for something like this. As good engineers should do.
            time_match = re.search(r"(.*?)\s*-\s*(.*)", time_part)
            if time_match:
                open_time_str = time_match.group(1).strip()
                close_time_str = time_match.group(2).strip()

                # Add entries for each day in the range
                for day in days:
                    result.append(
                        {
                            "restaurant_name": restaurant_name,
                            "day_of_week": day,
                            "open_time": parse_time(open_time_str),
                            "close_time": parse_time(close_time_str),
                        }
                    )

    return pd.DataFrame(result)


if __name__ == "__main__":
    df = pd.read_csv("data/restaurants.csv")
    transformed_df = transform_hours_data(df)
    # Save to csv, just easier than working with dbs for small datasets.
    transformed_df.to_csv("data/restaurants_transformed.csv", index=False)
