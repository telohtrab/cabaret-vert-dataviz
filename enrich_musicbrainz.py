import requests
#import pprint
import csv
import time

# Search for an artist on MusicBrainz and return their metadata (country, origin, type, id)
def search_artist(name):

    # HTTP request to the MusicBrainz API
    url = "https://musicbrainz.org/ws/2/artist/"
    response = requests.get(url, params={"query": f"artist:{name}", "fmt": "json"}).json()
    if not response.get('artists', []):
        return None

    # Sort results by score descending to get the best match first
    response = sorted(response['artists'], key = lambda score: score.get('score', 0), reverse=True)

    # Look for an exact name match in the top 10 results
    for r in response[:10]:
        if r.get('name', '').lower() == name.lower():
            response = [r]
            break
    else:
        # No exact match found — print suggestions and abort
        print("No exact match found for artist:", name)
        print("Best match found:", response[0]["name"])
        print("Following results were found:")
        for i, artist in enumerate(response):
            if i == 0:
                continue
            print(f"  {i + 1}. {artist['name']}")
            if i >= 5:
                break
        return None;

    # Extract useful fields (with fallback default if key is missing)
    mb_id = response[0].get('id', 'Unknown')
    artist_name = response[0].get('name', 'Unknown')
    artist_type = response[0].get('type', 'Unknown')
    artist_country = response[0].get('area', {}).get('name', 'Unknown')
    artist_origin = response[0].get('begin-area', {}).get('name', 'Unknown')

    artist_found = {
        "artist_name": artist_name,
        "type": artist_type,
        "country": artist_country,
        "origin": artist_origin,
        "mb_id": mb_id
    }
    time.sleep(1)  # 1-second pause to avoid overloading the API

    return artist_found;

##pprint.pprint(search_artist("PJ Harvey"))

existing_artists = {}

with open('data/performances.csv', 'r', encoding='utf-8') as csvfile:
    # Load already-processed artists to avoid duplicate API calls
    try:
        with open('data/raw/musicbrainz_results.csv', 'r', encoding='utf-8') as buffer:
            for row in csv.DictReader(buffer):
                if row['mb_id']:  # Only consider rows with a valid MusicBrainz ID
                    existing_artists[row['artist_name']] = row
    except FileNotFoundError:
        pass  # file absent on first run, start from scratch

    # Read the lineup and enrich each artist not yet processed
    with open('data/raw/musicbrainz_results.csv', 'a', newline='', encoding='utf-8') as buffer:
        writer = csv.DictWriter(buffer, fieldnames=["artist_name", "type", "country", "origin", "mb_id"])
        for row in csv.DictReader(csvfile):
            artist_name = row['artist_name']
            if artist_name not in existing_artists:
                existing_artists[artist_name] = search_artist(artist_name)
                if existing_artists[artist_name] is not None:
                    writer.writerow(existing_artists[artist_name])
                    print(f"Enriched artist written: {artist_name}")
                else:
                    writer.writerow({"artist_name": artist_name, "type": "", "country": "", "origin": "", "mb_id": ""})
                    print(f"Artist not found but written: {artist_name}")
            else:
                print(f"Artist {artist_name} already exists in the database, skipping API call.")
