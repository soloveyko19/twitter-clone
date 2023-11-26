import os
from dotenv import load_dotenv

load_dotenv()

# Main environment variables
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_DB = os.environ.get("POSTGRES_DB")

# Test enviroment variables
TESTING = os.environ.get("TESTING")
TEST_POSTGRES_USER = os.environ.get("TEST_POSTGRES_USER")
TEST_POSTGRES_PASSWORD = os.environ.get("TEST_POSTGRES_PASSWORD")
TEST_POSTGRES_HOST = os.environ.get("TEST_POSTGRES_HOST")
TEST_POSTGRES_DB = os.environ.get("TEST_POSTGRES_DB")
