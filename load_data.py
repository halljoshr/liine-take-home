"""
Script to load restaurant data from CSV into PostgreSQL database.
"""

import pandas as pd
from database import SessionLocal, RestaurantHours
from parse_data import transform_hours_data
import logging
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def wait_for_db(max_retries: int = 5, retry_interval: int = 5) -> None:
    """
    Wait for the database to be ready.

    Args:
        max_retries (int): Maximum number of retry attempts
        retry_interval (int): Time to wait between retries in seconds
    """
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("Database is ready!")
            return
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Database not ready. Retrying in {retry_interval} seconds... (Attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(retry_interval)
            else:
                logger.error("Could not connect to database after maximum retries")
                raise


def load_data_to_db():
    """
    Load restaurant data from CSV into PostgreSQL database.
    """
    try:
        # Wait for database to be ready
        wait_for_db()

        # Read and transform the data
        df = pd.read_csv("data/restaurants.csv")
        transformed_df = transform_hours_data(df)

        # Create database session
        db = SessionLocal()

        try:
            # Clear existing data
            db.query(RestaurantHours).delete()

            # Insert new data
            for _, row in transformed_df.iterrows():
                restaurant = RestaurantHours(
                    restaurant_name=row["restaurant_name"],
                    day_of_week=row["day_of_week"],
                    open_time=row["open_time"],
                    close_time=row["close_time"],
                )
                db.add(restaurant)

            # Commit the changes
            db.commit()
            logger.info("Successfully loaded data into database")

        except Exception as e:
            db.rollback()
            logger.error(f"Error loading data: {str(e)}")
            raise

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        raise


if __name__ == "__main__":
    load_data_to_db()
