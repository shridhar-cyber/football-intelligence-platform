from src.feature_engine.feature_context import FeatureContext
from src.feature_engine.recent_form import RecentFormFeature
from src.feature_engine.goal_statistics import GoalStatisticsFeature
from src.feature_engine.head_to_head import HeadToHeadFeature


class FeatureEngine:
    def __init__(self):
        self.features = [
            RecentFormFeature(),
            GoalStatisticsFeature(),
            HeadToHeadFeature(),
        ]

    def build(
        self,
        home_team,
        away_team,
        match_date=None,
        competition_name=None,
        last_n_matches=5,
    ):
        context = FeatureContext(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            competition_name=competition_name,
            last_n_matches=last_n_matches,
        )

        feature_vector = {}

        for feature in self.features:
            feature_vector.update(feature.compute(context))

        return feature_vector


if __name__ == "__main__":
    engine = FeatureEngine()

    features = engine.build(
        home_team="Brazil",
        away_team="Argentina",
        last_n_matches=5,
    )

    for feature_name, value in features.items():
        print(f"{feature_name}: {value}")