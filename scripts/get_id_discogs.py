import requests
import csv
import time
import os
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN")  # Get Discogs token from environment variable

# Search for an artist on Discogs by name and return their title and Discogs ID.
# If no exact match is found, displays the top 10 results for manual selection.
# Returns (name, 'x') if the user skips or no results are found.
def search_artist(name):

    url = "https://api.discogs.com/database/search"
    headers = {"Authorization": f"Discogs token={DISCOGS_TOKEN}"}
    params = {"q": name, "type": "artist", "per_page": 10}
    response = requests.get(url, headers=headers, params=params).json()
    if response['results'] and response['results'][0]['title'].lower() == name.lower():
        return response['results'][0]['title'], response['results'][0]['id']
    else:
        # No exact match — show top results for manual selection
        print(f"{name} not found, 10 first results out of {len(response['results'])}:")
        for i in range(0, min(10, len(response['results']))):
            print(i+1, ") ", response['results'][i]['title'].ljust(30), "\t | \t", response['results'][i]['uri'])
        choix = int(input("Enter the number of the correct artist (or 0 to skip): "))
        if 1 <= choix <= 10:
            return response['results'][choix-1]['title'], response['results'][choix-1]['id']
        else:
            print(f"Artist '{name}' not found.")
            return name, 'x'

existing_artists = {}

# Load all unique artists from the backup file
with open('data/raw/uniqueartists_backup.csv', 'r', encoding='utf-8') as infile:
    existing_artists = list(csv.DictReader(infile))

# Write enriched results to a new file to avoid data loss
with open('data/raw/uniqueartists_new.csv', 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames= existing_artists[0].keys())
    writer.writeheader()
    for artist in existing_artists:
        if artist['discogs_id']:  # Skip artists that already have a Discogs ID or are marked 'x'
            writer.writerow(artist)
            continue
        else:
            name, discogs_id = search_artist(artist['artist_name'])
            artist['discogs_id'] = discogs_id
            writer.writerow(artist)
            outfile.flush()  # Write to disk immediately to allow resuming after interruption
            print(f"Processed: {artist['artist_name']} - Discogs ID: {discogs_id}")
            time.sleep(1)  # Respect Discogs rate limit (60 requests/minute)
