from src.feature_engine.base_feature import BaseFeature
from src.repositories.match_repository import MatchRepository


class GoalStatisticsFeature(BaseFeature):
    """
    Calculates recent attacking and defensive goal statistics.
    """

    def __init__(self):
        self.match_repo = MatchRepository()

    def compute(self, context):
        home_matches = self.match_repo.get_last_n_matches_by_team(
            context.home_team,
            context.last_n_matches
        )

        away_matches = self.match_repo.get_last_n_matches_by_team(
            context.away_team,
            context.last_n_matches
        )

        home_stats = self._calculate_stats(home_matches, context.home_team)
        away_stats = self._calculate_stats(away_matches, context.away_team)

        return {
            "home_avg_goals_scored": home_stats["avg_goals_scored"],
            "away_avg_goals_scored": away_stats["avg_goals_scored"],
            "home_avg_goals_conceded": home_stats["avg_goals_conceded"],
            "away_avg_goals_conceded": away_stats["avg_goals_conceded"],
            "attacking_difference": round(
                home_stats["avg_goals_scored"]
                - away_stats["avg_goals_scored"],
                3
            ),
            "defensive_difference": round(
                away_stats["avg_goals_conceded"]
                - home_stats["avg_goals_conceded"],
                3
            ),
            "home_clean_sheet_rate": home_stats["clean_sheet_rate"],
            "away_clean_sheet_rate": away_stats["clean_sheet_rate"],
            "home_scoring_rate": home_stats["scoring_rate"],
            "away_scoring_rate": away_stats["scoring_rate"],
        }

    def _calculate_stats(self, matches, team_name):
        if not matches:
            return {
                "avg_goals_scored": 0.0,
                "avg_goals_conceded": 0.0,
                "clean_sheet_rate": 0.0,
                "scoring_rate": 0.0,
            }

        goals_scored = 0
        goals_conceded = 0
        clean_sheets = 0
        matches_scored_in = 0

        for match in matches:
            is_home = team_name.lower() == match["home_team"].lower()

            if is_home:
                goals_for = match["home_score"]
                goals_against = match["away_score"]
            else:
                goals_for = match["away_score"]
                goals_against = match["home_score"]

            goals_scored += goals_for
            goals_conceded += goals_against

            if goals_against == 0:
                clean_sheets += 1

            if goals_for > 0:
                matches_scored_in += 1

        total_matches = len(matches)

        return {
            "avg_goals_scored": round(goals_scored / total_matches, 3),
            "avg_goals_conceded": round(goals_conceded / total_matches, 3),
            "clean_sheet_rate": round(clean_sheets / total_matches, 3),
            "scoring_rate": round(matches_scored_in / total_matches, 3),
        }