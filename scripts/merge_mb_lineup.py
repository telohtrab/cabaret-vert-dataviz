import csv

results_dict = {}
lineup_artists = []

# Load MusicBrainz metadata into a dict keyed by lowercase artist name
with open('../data/raw/uniqueartists_backup.csv', 'r', encoding='utf-8') as results:
    results_dict = {row['artist_name'].lower(): row for row in csv.DictReader(results)}

# Load all performance rows into memory
with open('../data/performances_backup.csv', 'r', encoding='utf-8') as lineup:
    lineup_artists = list(csv.DictReader(lineup))

# Write merged output to a new file to avoid data loss if something goes wrong
with open('../data/performances_new.csv', 'w', newline='', encoding='utf-8') as merge:
    fieldnames = list(lineup_artists[0].keys())
    writer = csv.DictWriter(merge, fieldnames=fieldnames)
    writer.writeheader()

    for row in lineup_artists:
        # Update performance row with MusicBrainz fields (case-insensitive match)
        row.update(results_dict.get(row['artist_name'].lower(), {}))
        writer.writerow(row)
        print(row, " merged successfully")