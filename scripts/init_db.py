import sqlite3

# Create the SQLite database and all tables for the Cabaret Vert dataset
conn = sqlite3.connect('../data/cabaret_vert.db')
cursor = conn.cursor()

cursor.execute("""
                    CREATE TABLE IF NOT EXISTS genres (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE
                    )
               """)

cursor.execute("""
                    CREATE TABLE IF NOT EXISTS artists (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            country TEXT,
                            origin TEXT,
                            artist_type TEXT,
                            genre_1 INTEGER REFERENCES genres(id),
                            genre_2 INTEGER REFERENCES genres(id),
                            mb_id TEXT
                    )
               """)

cursor.execute("""
                    CREATE TABLE IF NOT EXISTS editions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            year INTEGER NOT NULL UNIQUE,
                            start_date TEXT,
                            end_date TEXT,
                            attendance INTEGER
                    )
                """)

cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE
                    )
                """)

cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performances (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            edition_id INTEGER REFERENCES editions(id),
                            stage_id INTEGER REFERENCES stages(id),
                            artist_id INTEGER REFERENCES artists(id),
                            cancelled INTEGER DEFAULT 0,
                            replacement_for_id INTEGER REFERENCES performances(id),
                            performance_date TEXT,
                            notes TEXT,
                            start_time TEXT,
                            end_time TEXT
                    )
                """)

conn.commit()
conn.close()

print("Base de données créée avec succès !")