### Liine Take Home 

__Python is preferred, but if you feel unable to complete it using python, use whatever programming language you feel most comfortable in.__

Build an API with an endpoint which takes a single parameter, a datetime string, and returns a list of restaurant names which are open on that date and time. You are provided a dataset in the form of a CSV file of restaurant names and a human-readable, string-formatted list of open hours. Store this data in whatever way you think is best. Optimized solutions are great, but correct solutions are more important. Make sure whatever solution you come up with can account for restaurants with hours not included in the examples given in the CSV. Please include all tests you think are needed.

### Assumptions:
* If a day of the week is not listed, the restaurant is closed on that day
* All times are local — don't worry about timezone-awareness
* The CSV file will be well-formed, assume all names and hours are correct

### Want bonus points? Here are a few things we would really like to see:
1. A Dockerfile and the ability to run this in a container

If you have any questions, let me know. Use git to track your progress, and push your solution to a github repository (public or if private just give me access @sharpmoose)

### Project Structure
- `main.py`: FastAPI application with the main endpoint
- `database.py`: SQLAlchemy models and database configuration
- `parse_data.py`: Script to parse and transform the restaurant hours data
- `load_data.py`: Script to load data from CSV into PostgreSQL
- `docker-compose.yml`: Docker Compose configuration for the application and database

### Running the Application

#### Using Docker Compose (Recommended)
```bash
# Build and start the containers
docker-compose up --build

# The API will be available at http://localhost:5555
```

#### Manual Setup
1. Install dependencies:
```bash
uv sync
```

2. Set up PostgreSQL database:
```bash
# Create database
createdb restaurants

# Set environment variable
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/restaurants"
```

3. Load data and run the application:
```bash
# Load data into database
uv run load_data.py

# Run the application
uv run main.py
```

### API Usage
The API provides a single endpoint:

```
GET /restaurants?datetime_str=YYYY-MM-DD HH:MM:SS
```

Example:
```bash
curl "http://localhost:5555/restaurants?datetime_str=2024-03-20%2014:30:00"
```

```
# Load Data with Postman
localhost:5555/load-data

# Get Data with Postman
localhost:5555/restaurants?datetime_str=2024-03-20 14:30:00
```

### Decisions / Observations

- Used FastAPI over Django because its better/faster to get these smaller projects rolling (Could rewrite in Django if you want me to)
- Implemented PostgreSQL for robust data storage and querying capabilities
- Used SQLAlchemy as the ORM for type-safe database operations
- Used uv as my package manager. Been exploring it lately.
- Added Docker Compose for easy deployment and development (docker with uv was a choice though, first time with that)
- Implemented proper error handling and logging
- Added data loading script to handle initial data population
- I used Postman to test the API endpoints
- Used pandas because I am a data person and grew up with it. There are other options.
- Tried to add some logging for debug level because I hate print statements leftover.

### TODO / Future expansion
1. Add more error handling
1. Add tests
1. Add data validation
1. Add health check endpoint
1. Move code to relevant places.
1. Receive more/different data sources
1. Might want to check if having multiple rows with same info but different times breaks anything
