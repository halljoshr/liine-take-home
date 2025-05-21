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
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

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


def load_data_to_db(
    df: pd.DataFrame = pd.read_csv("data/restaurants.csv"),
):
    """
    Load restaurant data from CSV into PostgreSQL database.
    Uses UPSERT to handle duplicate entries.
    """
    try:
        # Wait for database to be ready
        wait_for_db()

        # Read and transform the data
        # In theory we would want to allow us to give this a path to the csv file but if
        # I go down every expansion rabbit hole I will not finish in a timely manner.
        transformed_df = transform_hours_data(df)

        db: Session = SessionLocal()

        try:
            # Convert DataFrame to list of dictionaries
            records = transformed_df.to_dict("records")

            # Create insert statement with ON CONFLICT DO NOTHING
            stmt = insert(RestaurantHours).values(records)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[
                    "restaurant_name",
                    "day_of_week",
                    "open_time",
                    "close_time",
                ]
            )

            # Execute the statement
            db.execute(stmt)

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
