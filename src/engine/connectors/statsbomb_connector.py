from src.engine.base_connector import BaseConnector

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


class StatsBombConnector(BaseConnector):
    def __init__(self, category="international"):
        super().__init__(name="statsbomb")
        self.category = category

    def download(self):
        print("[StatsBomb] Downloading competitions and matches...")
        download_competitions()
        create_default_config()
        select_competitions(self.category)
        download_matches_for_selected_competitions()

    def validate(self):
        print("[StatsBomb] Validating downloaded data...")
        # Simple validation for now.
        # Later we will check required columns, missing values, duplicates, etc.
        pass

    def transform(self):
        print("[StatsBomb] Transforming data into registries...")
        generate_team_registry()
        generate_match_registry()

    def save(self):
        print("[StatsBomb] Saving processed data...")
        # Current functions already save CSV files.
        # Later this will save into database/warehouse.
        pass