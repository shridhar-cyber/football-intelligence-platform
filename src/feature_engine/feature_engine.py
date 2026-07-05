from src.feature_engine.feature_context import FeatureContext
from src.feature_engine.recent_form import RecentFormFeature


class FeatureEngine:
    def __init__(self):
        self.features = [
            RecentFormFeature()
        ]

    def build(self, home_team, away_team, match_date=None, competition_name=None):
        context = FeatureContext(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            competition_name=competition_name
        )

        feature_vector = {}

        for feature in self.features:
            feature_vector.update(feature.compute(context))

        return feature_vector


if __name__ == "__main__":
    engine = FeatureEngine()

    features = engine.build(
        home_team="Brazil",
        away_team="Argentina"
    )

    print(features)