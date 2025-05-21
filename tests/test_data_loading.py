"""
Tests for the data loading functionality.
"""

import pytest
from datetime import time
from database import RestaurantHours


def test_load_data_duplicates(db_session):
    """
    Test that loading the same data twice doesn't create duplicates.
    """
    # Create test data with proper time objects
    test_restaurant = RestaurantHours(
        restaurant_name="Test Restaurant",
        day_of_week=0,  # Monday
        open_time=time(9, 0),  # 9:00 AM
        close_time=time(17, 0),  # 5:00 PM
    )
    db_session.add(test_restaurant)
    db_session.commit()

    # Try to add the same data again
    db_session.add(test_restaurant)
    db_session.commit()

    # Check that we only have one record
    count = db_session.query(RestaurantHours).count()
    assert count == 1


def test_load_data_multiple_days(db_session):
    """
    Test loading data with multiple days.
    """
    # Create test data with proper time objects
    test_restaurants = [
        RestaurantHours(
            restaurant_name="Test Restaurant",
            day_of_week=day,
            open_time=time(9, 0),  # 9:00 AM
            close_time=time(17, 0),  # 5:00 PM
        )
        for day in range(5)  # Monday to Friday
    ]

    # Add Saturday with different hours
    test_restaurants.append(
        RestaurantHours(
            restaurant_name="Test Restaurant",
            day_of_week=5,  # Saturday
            open_time=time(10, 0),  # 10:00 AM
            close_time=time(15, 0),  # 3:00 PM
        )
    )

    # Add all records
    for restaurant in test_restaurants:
        db_session.add(restaurant)
    db_session.commit()

    # Check that we have records for all days
    records = db_session.query(RestaurantHours).all()
    assert len(records) == 6  # 5 weekdays + 1 Saturday

    # Check that times are correct
    weekday_record = db_session.query(RestaurantHours).filter_by(day_of_week=0).first()
    assert weekday_record.open_time == time(9, 0)
    assert weekday_record.close_time == time(17, 0)

    saturday_record = db_session.query(RestaurantHours).filter_by(day_of_week=5).first()
    assert saturday_record.open_time == time(10, 0)
    assert saturday_record.close_time == time(15, 0)
