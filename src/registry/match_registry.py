import pandas as pd
from pathlib import Path

MATCHES_FILE = Path("data/processed/statsbomb/matches.csv")
TEAMS_FILE = Path("data/processed/registry/teams.csv")
OUTPUT_FILE = Path("data/processed/registry/matches.csv")


def generate_match_registry():
    matches_df = pd.read_csv(MATCHES_FILE)
    teams_df = pd.read_csv(TEAMS_FILE)

    team_map = dict(zip(teams_df["source_team_id"], teams_df["fi_team_id"]))

    matches_df["home_fi_team_id"] = matches_df["home_team_id"].map(team_map)
    matches_df["away_fi_team_id"] = matches_df["away_team_id"].map(team_map)

    clean_matches = matches_df[
        [
            "match_id",
            "competition_id",
            "season_id",
            "competition_name",
            "season_name",
            "match_date",
            "kick_off",
            "home_fi_team_id",
            "home_team",
            "away_fi_team_id",
            "away_team",
            "home_score",
            "away_score",
            "stadium",
            "referee",
        ]
    ]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean_matches.to_csv(OUTPUT_FILE, index=False)

    print("Match registry created.")
    print(f"Total matches: {len(clean_matches)}")
    print(f"Saved at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_match_registry()