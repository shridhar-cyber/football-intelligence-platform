import json
import pandas as pd
from pathlib import Path

COMPETITIONS_FILE = Path("data/processed/statsbomb/competitions.csv")
CONFIG_FILE = Path("config/competitions.json")
OUTPUT_FILE = Path("data/processed/statsbomb/selected_competitions.csv")


DEFAULT_CONFIG = {
    "international": [
        "FIFA World Cup",
        "UEFA Euro",
        "Copa America",
        "African Cup of Nations"
    ],
    "club": [
        "Premier League",
        "La Liga",
        "Serie A",
        "1. Bundesliga",
        "Ligue 1",
        "Champions League",
        "UEFA Europa League"
    ],
    "india": [
        "Indian Super league"
    ]
}


def create_default_config():
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

        print(f"Created config file: {CONFIG_FILE}")
    else:
        print(f"Config already exists: {CONFIG_FILE}")


def select_competitions(category: str):
    if not COMPETITIONS_FILE.exists():
        raise FileNotFoundError("Run statsbomb_connector.py first.")

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    if category not in config:
        raise ValueError(f"Category not found. Available: {list(config.keys())}")

    selected_names = config[category]

    df = pd.read_csv(COMPETITIONS_FILE)

    selected_df = df[df["competition_name"].isin(selected_names)]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    selected_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSelected category: {category}")
    print(selected_df[[
        "competition_id",
        "season_id",
        "competition_name",
        "season_name"
    ]])


if __name__ == "__main__":
    create_default_config()

    # Start with international football
    select_competitions("international")