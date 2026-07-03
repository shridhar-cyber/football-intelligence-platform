from src.ingestion.statsbomb_connector import (
    download_competitions,
    download_matches_for_selected_competitions,
)

from src.ingestion.competition_manager import (
    create_default_config,
    select_competitions,
)

from src.registry.team_registry import generate_team_registry
from src.registry.match_registry import generate_match_registry


class FootballEngine:
    def __init__(self, category="international"):
        self.category = category

    def sync(self):
        print("\nStarting Football Intelligence Data Engine...\n")

        print("Step 1: Downloading StatsBomb competitions...")
        download_competitions()

        print("\nStep 2: Loading selected competitions...")
        create_default_config()
        select_competitions(self.category)

        print("\nStep 3: Downloading matches...")
        download_matches_for_selected_competitions()

        print("\nStep 4: Building team registry...")
        generate_team_registry()

        print("\nStep 5: Building match registry...")
        generate_match_registry()

        print("\nFootball Data Engine sync completed successfully!")


if __name__ == "__main__":
    engine = FootballEngine(category="international")
    engine.sync()