"""
Tests for the restaurant API endpoints.
"""

import pytest
from datetime import datetime, time
from database import RestaurantHours


def test_get_restaurants_empty_db(client):
    """
    Test getting restaurants when database is empty.
    """
    response = client.get("/restaurants?datetime_str=2024-03-20%2014:30:00")
    assert response.status_code == 200
    assert response.json() == {"restaurant_names": []}


def test_get_restaurants_invalid_datetime(client):
    """
    Test getting restaurants with invalid datetime format.
    """
    response = client.get("/restaurants?datetime_str=invalid-datetime")
    assert response.status_code == 400
    assert "Invalid datetime format" in response.json()["detail"]


def test_get_restaurants_with_data(client, db_session):
    """
    Test getting restaurants with some test data.
    """
    # Add test data
    test_restaurant = RestaurantHours(
        restaurant_name="Test Restaurant",
        day_of_week=2,  # Wednesday
        open_time=time(9, 0),  # 9:00 AM
        close_time=time(17, 0),  # 5:00 PM
    )
    db_session.add(test_restaurant)
    db_session.commit()

    # Test during open hours
    response = client.get("/restaurants?datetime_str=2024-03-20%2014:30:00")
    assert response.status_code == 200
    assert "Test Restaurant" in response.json()["restaurant_names"]

    # Test during closed hours
    response = client.get("/restaurants?datetime_str=2024-03-20%2018:30:00")
    assert response.status_code == 200
    assert "Test Restaurant" not in response.json()["restaurant_names"]


def test_load_data_endpoint(client):
    """
    Test the data loading endpoint.
    """
    response = client.post("/load-data")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Data loading started in background",
        "status": "processing",
    }
