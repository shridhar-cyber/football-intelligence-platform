from src.feature_engine.base_feature import BaseFeature
from src.repositories.elo_repository import EloRepository


class EloFeature(BaseFeature):

    def __init__(self):
        self.repository = EloRepository()

    def compute(self, context):

        home_elo = self.repository.get_team_rating(
            context.home_team
        )

        away_elo = self.repository.get_team_rating(
            context.away_team
        )

        return {
            "home_elo": home_elo,
            "away_elo": away_elo,
            "elo_difference": round(
                home_elo - away_elo,
                2,
            ),
        }