from src.warehouse.database import Database


class WarehouseSchema:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.connect()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS matches")
        cursor.execute("DROP TABLE IF EXISTS teams")
        cursor.execute("DROP TABLE IF EXISTS seasons")
        cursor.execute("DROP TABLE IF EXISTS competitions")

        cursor.execute("""
        CREATE TABLE competitions (
            competition_id INTEGER PRIMARY KEY,
            competition_name TEXT NOT NULL,
            country_name TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE seasons (
            season_id INTEGER,
            competition_id INTEGER,
            season_name TEXT NOT NULL,
            PRIMARY KEY (competition_id, season_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE teams (
            team_id TEXT PRIMARY KEY,
            team_name TEXT NOT NULL,
            source TEXT,
            source_team_id INTEGER
        )
        """)

        cursor.execute("""
        CREATE TABLE matches (
            match_id INTEGER PRIMARY KEY,
            competition_id INTEGER,
            season_id INTEGER,
            competition_name TEXT,
            season_name TEXT,
            match_date TEXT,
            kick_off TEXT,
            home_team_id TEXT,
            home_team TEXT,
            away_team_id TEXT,
            away_team TEXT,
            home_score INTEGER,
            away_score INTEGER,
            stadium TEXT,
            referee TEXT
        )
        """)

        self.conn.commit()
        print("Football Warehouse schema created successfully.")