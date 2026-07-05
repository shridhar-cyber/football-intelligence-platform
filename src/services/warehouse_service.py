from pathlib import Path
import pandas as pd

from src.warehouse.database import Database
from src.warehouse.schema import WarehouseSchema


WAREHOUSE_DIR = Path("data/warehouse")


TABLE_COLUMNS = {
    "competitions": ["competition_id", "competition_name", "country_name"],
    "seasons": ["season_id", "competition_id", "season_name"],
    "teams": ["team_id", "team_name", "source", "source_team_id"],
    "matches": [
        "match_id", "competition_id", "season_id", "competition_name",
        "season_name", "match_date", "kick_off",
        "home_team_id", "home_team", "away_team_id", "away_team",
        "home_score", "away_score", "stadium", "referee"
    ],
}


class WarehouseService:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.connect()

    def initialize(self):
        print("\nInitializing Football Warehouse...\n")
        WarehouseSchema().create_tables()
        print("Schema initialized.\n")

    def load_table(self, csv_file, table_name):
        csv_path = WAREHOUSE_DIR / csv_file

        if not csv_path.exists():
            print(f"{csv_file} not found.")
            return

        df = pd.read_csv(csv_path)

        required_columns = TABLE_COLUMNS[table_name]
        df = df[required_columns]

        self.conn.execute(f"DELETE FROM {table_name}")

        df.to_sql(
            table_name,
            self.conn,
            if_exists="append",
            index=False
        )

        self.conn.commit()
        print(f"{table_name:<15} Loaded ({len(df)} rows)")

    def load(self):
        print("Loading warehouse tables...\n")

        self.load_table("competitions.csv", "competitions")
        self.load_table("seasons.csv", "seasons")
        self.load_table("teams.csv", "teams")
        self.load_table("matches.csv", "matches")

        print("\nAll warehouse tables loaded.")

    def verify(self):
        print("\nVerifying Warehouse...\n")

        cursor = self.conn.cursor()

        for table in TABLE_COLUMNS.keys():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:<15} {count} rows")

        print("\nVerification complete.")

    def run(self):
        self.initialize()
        self.load()
        self.verify()


if __name__ == "__main__":
    WarehouseService().run()