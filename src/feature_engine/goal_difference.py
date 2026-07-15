from src.feature_engine.base_feature import BaseFeature
from src.feature_engine.goal_statistics import GoalStatisticsFeature


class GoalDifferenceFeature(BaseFeature):
    """
    Computes goal-difference based features using
    the averages already calculated by GoalStatisticsFeature.
    """

    def compute(self, context):

        goal_stats = GoalStatisticsFeature().compute(context)

        home_goal_difference = (
            goal_stats["home_avg_goals_scored"]
            - goal_stats["home_avg_goals_conceded"]
        )

        away_goal_difference = (
            goal_stats["away_avg_goals_scored"]
            - goal_stats["away_avg_goals_conceded"]
        )

        return {
            "home_goal_difference": round(
                home_goal_difference,
                3,
            ),
            "away_goal_difference": round(
                away_goal_difference,
                3,
            ),
            "goal_difference_difference": round(
                home_goal_difference
                - away_goal_difference,
                3,
            ),
        }