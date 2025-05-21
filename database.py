from sqlalchemy import create_engine, Column, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
import os

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/restaurants"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


class RestaurantHours(Base):
    __tablename__ = "restaurant_hours"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String, index=True)
    day_of_week = Column(Integer)  # 0 = Monday, 6 = Sunday
    open_time = Column(Time)
    close_time = Column(Time)

    # Add unique constraint to prevent duplicates
    __table_args__ = (
        UniqueConstraint(
            "restaurant_name",
            "day_of_week",
            "open_time",
            "close_time",
            name="unique_restaurant_hours",
        ),
    )


# Create all tables
Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    """
    Dependency for getting database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
