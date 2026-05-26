import requests
import csv
import time
import os
import pprint
from collections import Counter
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN")  # Get Discogs token from environment variable

def search_genre(artist_id, artist_name):
    
    url = f"https://api.discogs.com/artists/{artist_id}/releases?sort=year&sort_order=desc&per_page=50"
    headers = {"Authorization": f"Discogs token={DISCOGS_TOKEN}"}
    master_raw = requests.get(url, headers=headers)
    print(master_raw.headers.get('X-Discogs-Ratelimit-Remaining'))
    response = master_raw.json()

    genres = Counter()  # Use Counter to aggregate genre counts
    styles = Counter()

    releases = sorted(
    [r for r in response.get('releases', []) if r.get('type') == 'master' and r.get('year', 0) > 0 and r.get('role') == 'Main'],
        key=lambda r: r.get('year', 0),
        reverse=True
    )[:8] # Limit to first 8 master releases to avoid too many API calls
    if not releases:
        releases = sorted(
             [r for r in response.get('releases', []) if r.get('type') == 'release' and r.get('year', 0) > 0 and r.get('role') == 'Main'],
            key=lambda r: r.get('year', 0),
            reverse=True
    )[:8] # If no master releases, take first 8 releases
    if not releases:
        releases = sorted(
        [r for r in response.get('releases', []) if r.get('type') == 'master' and r.get('year', 0) > 0],
        key=lambda r: r.get('year', 0),
        reverse=True
    )[:5] # If no main role releases, take first 5 master releases
    if not releases:
        releases = sorted(
        [r for r in response.get('releases', []) if r.get('type') == 'release' and r.get('year', 0) > 0],
        key=lambda r: r.get('year', 0),
        reverse=True
    )[:5] # If no main role master releases, take first 5 releases regardless of role
        
    print("=================================")
    print(f"Fetching releases for artist {artist_id} - {artist_name}")
    for r in releases:  
        master_id = r.get('id')
        if master_id:
            release_type = r.get('type')
            url = f"https://api.discogs.com/masters/{r['id']}" if release_type == 'master' else f"https://api.discogs.com/releases/{r['id']}"
            master_raw = requests.get(url, headers=headers)

            if master_raw.status_code == 200:
                master_response = master_raw.json()
            else:
                print(f"Error {master_raw.status_code} for master {master_id}")
                continue

            print(f"  - {master_response.get('title')} ({master_response.get('year')}) [{r.get('type')}] - Style : {master_response.get('styles')}")

            genres.update(master_response.get('genres', []))
            styles.update(master_response.get('styles', []))
            time.sleep(1)  # Respect Discogs rate limit (60 requests/minute)
    

    top_genres = genres.most_common(1)[0][0] if genres else 'Unknown'
    top_styles = [s[0] for s in styles.most_common(3)] if styles else ['Unknown']

    return top_genres, top_styles

with open('data/raw/uniqueartists_backup.csv', 'r', encoding='utf-8') as csvfile:
    with open('data/raw/uniqueartists_new.csv', 'w', encoding='utf-8', newline='') as outfile:
        artists = list(csv.DictReader(csvfile))
        fieldnames = artists[0].keys()

        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()

        for artist in artists:
            if artist['discogs_id'] and artist['discogs_id'] != 'x' and not artist['genre']:
                genre, styles = search_genre(artist['discogs_id'], artist['artist_name'])
                artist['genre'] = genre
                artist['style_1'] = styles[0] if len(styles) > 0 else ''
                artist['style_2'] = styles[1] if len(styles) > 1 else ''
                artist['style_3'] = styles[2] if len(styles) > 2 else ''    
                print(f"Enriched artist: {artist['artist_name']} - Genre: {genre} - Styles: {styles}")
            
            writer.writerow(artist) # Write the (possibly enriched) artist data to the new CSV file
            outfile.flush()  # Ensure data is written to file after each artist