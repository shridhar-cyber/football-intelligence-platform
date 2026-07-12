from src.feature_engine.base_feature import BaseFeature
from src.repositories.match_repository import MatchRepository


class HomeAwayFormFeature(BaseFeature):
    """
    Calculates home-only performance for the home team
    and away-only performance for the away team.
    """

    def __init__(self):
        self.match_repo = MatchRepository()

    def compute(self, context):
        home_matches = self.match_repo.get_home_matches(
            context.home_team,
            context.last_n_matches
        )

        away_matches = self.match_repo.get_away_matches(
            context.away_team,
            context.last_n_matches
        )

        home_stats = self._calculate_stats(
            home_matches,
            context.home_team,
            is_home=True
        )

        away_stats = self._calculate_stats(
            away_matches,
            context.away_team,
            is_home=False
        )

        return {
            "home_home_form": home_stats["form"],
            "away_away_form": away_stats["form"],
            "home_home_avg_goals": home_stats["avg_goals_scored"],
            "away_away_avg_goals": away_stats["avg_goals_scored"],
            "home_home_avg_conceded": home_stats["avg_goals_conceded"],
            "away_away_avg_conceded": away_stats["avg_goals_conceded"],
            "home_away_form_difference": round(
                home_stats["form"] - away_stats["form"],
                3
            ),
        }

    def _calculate_stats(self, matches, team_name, is_home):
        if not matches:
            return {
                "form": 0.0,
                "avg_goals_scored": 0.0,
                "avg_goals_conceded": 0.0,
            }

        points = 0
        goals_scored = 0
        goals_conceded = 0

        for match in matches:
            if is_home:
                goals_for = match["home_score"]
                goals_against = match["away_score"]
            else:
                goals_for = match["away_score"]
                goals_against = match["home_score"]

            goals_scored += goals_for
            goals_conceded += goals_against

            if goals_for > goals_against:
                points += 3
            elif goals_for == goals_against:
                points += 1

        total_matches = len(matches)

        return {
            "form": round(points / (total_matches * 3), 3),
            "avg_goals_scored": round(goals_scored / total_matches, 3),
            "avg_goals_conceded": round(goals_conceded / total_matches, 3),
        }