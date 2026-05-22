import requests
import csv
import time

load_dotenv()  # Load environment variables from .env file
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN")  # Get Discogs token from environment variable

