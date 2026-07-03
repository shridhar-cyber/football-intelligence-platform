import requests
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw/statsbomb")
PROCESSED_DIR = Path("data/processed/statsbomb")

BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
COMPETITIONS_URL = f"{BASE_URL}/competitions.json"


def download_competitions():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    response = requests.get(COMPETITIONS_URL)
    response.raise_for_status()

    data = response.json()

    pd.DataFrame(data).to_json(RAW_DIR / "competitions.json", orient="records", indent=2)
    pd.DataFrame(data).to_csv(PROCESSED_DIR / "competitions.csv", index=False)

    print("Competitions downloaded.")


def download_matches_for_selected_competitions():
    selected_file = PROCESSED_DIR / "selected_competitions.csv"

    if not selected_file.exists():
        raise FileNotFoundError("Run competition_manager.py first.")

    selected_df = pd.read_csv(selected_file)

    all_matches = []

    for _, row in selected_df.iterrows():
        competition_id = int(row["competition_id"])
        season_id = int(row["season_id"])

        url = f"{BASE_URL}/matches/{competition_id}/{season_id}.json"

        response = requests.get(url)
        response.raise_for_status()

        matches = response.json()

        for match in matches:
            all_matches.append({
                "match_id": match.get("match_id"),
                "competition_id": competition_id,
                "season_id": season_id,
                "competition_name": row["competition_name"],
                "season_name": row["season_name"],
                "match_date": match.get("match_date"),
                "kick_off": match.get("kick_off"),
                "home_team_id": match.get("home_team", {}).get("home_team_id"),
                "home_team": match.get("home_team", {}).get("home_team_name"),
                "away_team_id": match.get("away_team", {}).get("away_team_id"),
                "away_team": match.get("away_team", {}).get("away_team_name"),
                "home_score": match.get("home_score"),
                "away_score": match.get("away_score"),
                "stadium": match.get("stadium", {}).get("name") if match.get("stadium") else None,
                "referee": match.get("referee", {}).get("name") if match.get("referee") else None,
            })

    matches_df = pd.DataFrame(all_matches)

    matches_df.to_csv(PROCESSED_DIR / "matches.csv", index=False)

    print("Matches downloaded.")
    print(f"Total matches: {len(matches_df)}")
    print(PROCESSED_DIR / "matches.csv")


if __name__ == "__main__":
    download_competitions()
    download_matches_for_selected_competitions()