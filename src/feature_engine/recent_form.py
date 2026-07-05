from src.feature_engine.base_feature import BaseFeature
from src.repositories.match_repository import MatchRepository


class RecentFormFeature(BaseFeature):
    def __init__(self):
        self.match_repo = MatchRepository()

    def compute(self, context):
        home_matches = self.match_repo.get_matches_by_team(context.home_team)
        away_matches = self.match_repo.get_matches_by_team(context.away_team)

        home_form = self._calculate_form(home_matches, context.home_team, context.last_n_matches)
        away_form = self._calculate_form(away_matches, context.away_team, context.last_n_matches)

        return {
            "home_recent_form": home_form,
            "away_recent_form": away_form,
            "recent_form_difference": round(home_form - away_form, 3)
        }

    def _calculate_form(self, matches, team_name, last_n):
        matches = matches[:last_n]

        if not matches:
            return 0.0

        points = 0

        for match in matches:
            home_team = match["home_team"]
            away_team = match["away_team"]
            home_score = match["home_score"]
            away_score = match["away_score"]

            if team_name.lower() == home_team.lower():
                points += self._points(home_score, away_score)
            elif team_name.lower() == away_team.lower():
                points += self._points(away_score, home_score)

        return round(points / (last_n * 3), 3)

    def _points(self, goals_for, goals_against):
        if goals_for > goals_against:
            return 3
        if goals_for == goals_against:
            return 1
        return 0