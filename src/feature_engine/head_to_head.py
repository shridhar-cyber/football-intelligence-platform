from src.feature_engine.base_feature import BaseFeature
from src.repositories.match_repository import MatchRepository


class HeadToHeadFeature(BaseFeature):
    """
    Calculates historical head-to-head statistics between two teams.
    """

    def __init__(self):
        self.match_repo = MatchRepository()

    def compute(self, context):
        matches = self.match_repo.get_head_to_head(
            context.home_team,
            context.away_team
        )

        if not matches:
            return {
                "head_to_head_matches": 0,
                "home_h2h_wins": 0,
                "away_h2h_wins": 0,
                "h2h_draws": 0,
                "home_h2h_win_rate": 0.0,
                "away_h2h_win_rate": 0.0,
                "h2h_draw_rate": 0.0,
                "home_h2h_goal_difference": 0,
            }

        home_wins = 0
        away_wins = 0
        draws = 0
        home_goals = 0
        away_goals = 0

        for match in matches:
            if context.home_team.lower() == match["home_team"].lower():
                home_score = match["home_score"]
                away_score = match["away_score"]
            else:
                home_score = match["away_score"]
                away_score = match["home_score"]

            home_goals += home_score
            away_goals += away_score

            if home_score > away_score:
                home_wins += 1
            elif home_score < away_score:
                away_wins += 1
            else:
                draws += 1

        total_matches = len(matches)

        return {
            "head_to_head_matches": total_matches,
            "home_h2h_wins": home_wins,
            "away_h2h_wins": away_wins,
            "h2h_draws": draws,
            "home_h2h_win_rate": round(home_wins / total_matches, 3),
            "away_h2h_win_rate": round(away_wins / total_matches, 3),
            "h2h_draw_rate": round(draws / total_matches, 3),
            "home_h2h_goal_difference": home_goals - away_goals,
        }