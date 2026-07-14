from pathlib import Path

import pandas as pd


STATSBOMB_MATCHES = Path(
    "data/processed/registry/matches.csv"
)

FOOTBALL_DATA_MATCHES = Path(
    "data/processed/football_data/matches.csv"
)

OUTPUT_DIR = Path("data/processed/unified")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "matches.csv"


class UnifiedRegistryService:
    """
    Combines normalized match data from multiple sources into one registry.
    """

    TARGET_COLUMNS = [
        "match_id",
        "competition_id",
        "season_id",
        "competition_name",
        "season_name",
        "match_date",
        "kick_off",
        "home_team_id",
        "home_team",
        "away_team_id",
        "away_team",
        "home_score",
        "away_score",
        "stadium",
        "referee",
        "source",
    ]

    @staticmethod
    def _prepare_statsbomb(df):
        result = df.copy()

        if "source" not in result.columns:
            result["source"] = "statsbomb"

        return result

    @staticmethod
    def _prepare_football_data(df):
        result = df.copy()

        result["competition_id"] = None
        result["season_id"] = None
        result["home_team_id"] = None
        result["away_team_id"] = None
        result["stadium"] = None

        return result

    def build(self):
        if not STATSBOMB_MATCHES.exists():
            raise FileNotFoundError(
                f"Missing StatsBomb registry: {STATSBOMB_MATCHES}"
            )

        if not FOOTBALL_DATA_MATCHES.exists():
            raise FileNotFoundError(
                f"Missing Football-Data file: {FOOTBALL_DATA_MATCHES}"
            )

        statsbomb = pd.read_csv(STATSBOMB_MATCHES)
        football_data = pd.read_csv(FOOTBALL_DATA_MATCHES)

        statsbomb = self._prepare_statsbomb(statsbomb)
        football_data = self._prepare_football_data(football_data)

        for column in self.TARGET_COLUMNS:
            if column not in statsbomb.columns:
                statsbomb[column] = None

            if column not in football_data.columns:
                football_data[column] = None

        unified = pd.concat(
            [
                statsbomb[self.TARGET_COLUMNS],
                football_data[self.TARGET_COLUMNS],
            ],
            ignore_index=True,
        )

        unified = (
            unified
            .drop_duplicates(subset=["match_id"])
            .sort_values(["match_date", "match_id"])
            .reset_index(drop=True)
        )

        unified.to_csv(OUTPUT_FILE, index=False)

        print("Unified match registry created.")
        print(f"StatsBomb matches: {len(statsbomb)}")
        print(f"Football-Data matches: {len(football_data)}")
        print(f"Unified matches: {len(unified)}")
        print(f"Saved at: {OUTPUT_FILE}")

        print("\nSource distribution:")
        print(unified["source"].value_counts())

        return unified


if __name__ == "__main__":
    UnifiedRegistryService().build()