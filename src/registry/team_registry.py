import pandas as pd
from pathlib import Path

MATCHES_FILE = Path("data/processed/statsbomb/matches.csv")
OUTPUT_FILE = Path("data/processed/registry/teams.csv")


def generate_team_registry():
    if not MATCHES_FILE.exists():
        raise FileNotFoundError("matches.csv not found. Run statsbomb_connector.py first.")

    matches_df = pd.read_csv(MATCHES_FILE)

    home_teams = matches_df[["home_team_id", "home_team"]].rename(
        columns={"home_team_id": "source_team_id", "home_team": "team_name"}
    )

    away_teams = matches_df[["away_team_id", "away_team"]].rename(
        columns={"away_team_id": "source_team_id", "away_team": "team_name"}
    )

    teams_df = pd.concat([home_teams, away_teams], ignore_index=True)
    teams_df = teams_df.drop_duplicates().dropna()
    teams_df = teams_df.sort_values("team_name").reset_index(drop=True)

    teams_df["fi_team_id"] = [
        f"FI_TEAM_{i+1:06d}" for i in range(len(teams_df))
    ]

    teams_df["source"] = "statsbomb"
    teams_df["canonical_name"] = teams_df["team_name"]

    teams_df = teams_df[
        ["fi_team_id", "canonical_name", "source", "source_team_id", "team_name"]
    ]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    teams_df.to_csv(OUTPUT_FILE, index=False)

    print("Team registry created.")
    print(f"Total teams: {len(teams_df)}")
    print(f"Saved at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_team_registry()