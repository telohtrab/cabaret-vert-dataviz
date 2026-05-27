import requests
import csv
import time
import os

def get_gender_from_wikidata(mb_id):
    # Wikidata SPARQL query to fetch gender information for a given MusicBrainz ID
    url = "https://query.wikidata.org/sparql"
    query = f"""SELECT ?genderLabel ?artistLabel WHERE {{
                ?artist wdt:P434 "{mb_id}";
                wdt:P21 ?gender.
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}"""  

    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "cabaret-vert-dataviz/1.0"
    }
    response = requests.get(url, params={"query": query}, headers=headers)
    #print(response.status_code)

    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limited, waiting {retry_after}s...")
        time.sleep(retry_after)
        response = requests.get(url, params={"query": query}, headers=headers)

    data = response.json()

    ##print(data)

    bindings = data['results']['bindings']
    if bindings:
        gender = bindings[0]['genderLabel']['value']
        name = bindings[0]['artistLabel']['value']
    else:
        gender = ''
        name = ''

    time.sleep(1)  # 1-second pause to avoid overloading the API

    print(f"MusicBrainz ID: {mb_id}, Name: {name}, Gender: {gender}")

    return gender



with open('data/raw/uniqueartists_backup.csv', 'r', encoding='utf-8') as csvfile:
    current_gender = ''
    reader = csv.DictReader(csvfile)

    with open('data/raw/uniqueartists_new.csv', 'w', encoding='utf-8', newline='') as csvfile_out:
        writer = csv.DictWriter(csvfile_out, fieldnames=reader.fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()  # Write the header to the new CSV file

        for row in reader:
            mb_id = row['mb_id']
            artist_type = row['artist_type']
            gender = row['gender']
            if artist_type == 'Person' and mb_id and mb_id != 'Unknown' and gender == '':
                print("Getting gender for: \t\t\t", row['artist_name'])
                current_gender = get_gender_from_wikidata(mb_id)
                
                row['gender'] = current_gender
                writer.writerow(row)
            else:
                print("Skipping: \t\t\t\t", row['artist_name'])
                writer.writerow(row)
        
        

'''
#PJ Harvey 
get_gender_from_wikidata("e795e03d-b5d5-4a5f-834d-162cfb308a2c")
#Crystal Murray
get_gender_from_wikidata("28618ae8-bf38-45ab-8517-2fe79933aacf")
#Louis Tomlinson
get_gender_from_wikidata("6d390061-b3cd-4db3-b905-e56b7f5357fd")
#Marion Di Napoli
get_gender_from_wikidata("16966ee1-d327-46c0-a709-001d31b38a22")
'''