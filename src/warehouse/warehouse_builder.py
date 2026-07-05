import pandas as pd
from pathlib import Path

STATSBOMB_DIR = Path("data/processed/statsbomb")
REGISTRY_DIR = Path("data/processed/registry")
WAREHOUSE_DIR = Path("data/warehouse")


class WarehouseBuilder:
    def __init__(self):
        WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

    def build_competitions_table(self):
        competitions = pd.read_csv(STATSBOMB_DIR / "competitions.csv")

        competitions_clean = competitions[[
            "competition_id",
            "competition_name",
            "country_name"
        ]].drop_duplicates()

        competitions_clean.to_csv(WAREHOUSE_DIR / "competitions.csv", index=False)
        print("Created warehouse table: competitions.csv")

    def build_seasons_table(self):
        competitions = pd.read_csv(STATSBOMB_DIR / "competitions.csv")

        seasons_clean = competitions[[
            "season_id",
            "competition_id",
            "season_name"
        ]].drop_duplicates()

        seasons_clean.to_csv(WAREHOUSE_DIR / "seasons.csv", index=False)
        print("Created warehouse table: seasons.csv")

    def build_teams_table(self):
        teams = pd.read_csv(REGISTRY_DIR / "teams.csv")

        teams_clean = teams.rename(columns={
            "fi_team_id": "team_id",
            "canonical_name": "team_name"
        })

        teams_clean = teams_clean[[
            "team_id",
            "team_name",
            "source",
            "source_team_id"
        ]]

        teams_clean.to_csv(WAREHOUSE_DIR / "teams.csv", index=False)
        print("Created warehouse table: teams.csv")

    def build_matches_table(self):
        matches = pd.read_csv(REGISTRY_DIR / "matches.csv")

        matches_clean = matches.rename(columns={
            "home_fi_team_id": "home_team_id",
            "away_fi_team_id": "away_team_id"
        })

        matches_clean.to_csv(WAREHOUSE_DIR / "matches.csv", index=False)
        print("Created warehouse table: matches.csv")

    def build(self):
        print("\nBuilding Football Data Warehouse...\n")

        self.build_competitions_table()
        self.build_seasons_table()
        self.build_teams_table()
        self.build_matches_table()

        print("\nWarehouse build completed.")


if __name__ == "__main__":
    builder = WarehouseBuilder()
    builder.build()