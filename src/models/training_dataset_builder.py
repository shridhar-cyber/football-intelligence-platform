from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.repositories.match_repository import MatchRepository


OUTPUT_DIR = Path("data/features")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "training_dataset.csv"

INITIAL_ELO = 1500.0
K_FACTOR = 20.0
HOME_ADVANTAGE = 100.0


class TrainingDatasetBuilder:
    """
    Builds a leakage-free training dataset.

    Every row uses only information available before that match,
    including the teams' pre-match Elo ratings.
    """

    def __init__(self, last_n_matches=5):
        self.match_repo = MatchRepository()
        self.last_n_matches = last_n_matches
        self.elo_ratings = defaultdict(lambda: INITIAL_ELO)

    @staticmethod
    def _expected_score(rating_a, rating_b, home_advantage=0.0):
        return 1.0 / (
            1.0
            + 10.0
            ** (
                (
                    rating_b
                    - (rating_a + home_advantage)
                )
                / 400.0
            )
        )

    @staticmethod
    def _update_rating(rating, expected, actual):
        return rating + K_FACTOR * (actual - expected)

    def _update_elo_after_match(self, match):
        home_team = match["home_team"]
        away_team = match["away_team"]

        home_elo = self.elo_ratings[home_team]
        away_elo = self.elo_ratings[away_team]

        expected_home = self._expected_score(
            home_elo,
            away_elo,
            HOME_ADVANTAGE,
        )
        expected_away = 1.0 - expected_home

        if match["home_score"] > match["away_score"]:
            actual_home = 1.0
            actual_away = 0.0
        elif match["home_score"] < match["away_score"]:
            actual_home = 0.0
            actual_away = 1.0
        else:
            actual_home = 0.5
            actual_away = 0.5

        self.elo_ratings[home_team] = self._update_rating(
            home_elo,
            expected_home,
            actual_home,
        )

        self.elo_ratings[away_team] = self._update_rating(
            away_elo,
            expected_away,
            actual_away,
        )

    def _team_statistics(self, team_name, match_date):
        matches = self.match_repo.get_matches_by_team_before_date(
            team_name=team_name,
            before_date=match_date,
            n=self.last_n_matches,
        )

        if not matches:
            return {
                "form": 0.0,
                "avg_goals_scored": 0.0,
                "avg_goals_conceded": 0.0,
                "goal_difference": 0.0,
                "win_rate": 0.0,
            }

        points = 0
        wins = 0
        goals_scored = 0
        goals_conceded = 0

        for match in matches:
            is_home = (
                team_name.lower()
                == match["home_team"].lower()
            )

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
                wins += 1
            elif goals_for == goals_against:
                points += 1

        total = len(matches)

        return {
            "form": round(points / (total * 3), 4),

            "avg_goals_scored": round(goals_scored / total, 4),

            "avg_goals_conceded": round(goals_conceded / total, 4),

            "goal_difference": round(
                (goals_scored - goals_conceded) / total,
                4,
            ),

            "win_rate": round(wins / total, 4),
        }

    @staticmethod
    def _target(home_score, away_score):
        if home_score > away_score:
            return 0
        if home_score == away_score:
            return 1
        return 2

    def build(self):
        matches = self.match_repo.get_all_matches()

        matches = sorted(
            matches,
            key=lambda match: match["match_date"],
        )

        rows = []

        for match in matches:
            if (
                not match["match_date"]
                or match["home_score"] is None
                or match["away_score"] is None
            ):
                continue

            home_team = match["home_team"]
            away_team = match["away_team"]

            home_stats = self._team_statistics(
                home_team,
                match["match_date"],
            )

            away_stats = self._team_statistics(
                away_team,
                match["match_date"],
            )

            home_elo = self.elo_ratings[home_team]
            away_elo = self.elo_ratings[away_team]

            if (
                home_stats["form"] != 0.0
                or away_stats["form"] != 0.0
            ):
                rows.append({
                    "match_id": match["match_id"],
                    "match_date": match["match_date"],
                    "home_team": home_team,
                    "away_team": away_team,

                    "home_form": home_stats["form"],
                    "away_form": away_stats["form"],
                    "form_difference": round(
                        home_stats["form"]
                        - away_stats["form"],
                        4,
                    ),

                    "home_avg_goals_scored":
                        home_stats["avg_goals_scored"],
                    "away_avg_goals_scored":
                        away_stats["avg_goals_scored"],

                    "home_avg_goals_conceded":
                        home_stats["avg_goals_conceded"],
                    "away_avg_goals_conceded":
                        away_stats["avg_goals_conceded"],
                    
                    "home_goal_difference":
                        home_stats["goal_difference"],

                    "away_goal_difference":
                        away_stats["goal_difference"],

                    "goal_difference_difference":
                        round(
                            home_stats["goal_difference"]
                            - away_stats["goal_difference"],
                            4,
                        ),    
                    "home_win_rate":
                        home_stats["win_rate"],
                    "away_win_rate":
                        away_stats["win_rate"],

                    "home_elo": round(home_elo, 4),
                    "away_elo": round(away_elo, 4),
                    "elo_difference": round(
                        home_elo - away_elo,
                        4,
                    ),

                    "target": self._target(
                        match["home_score"],
                        match["away_score"],
                    ),
                })

            self._update_elo_after_match(match)

        dataset = pd.DataFrame(rows)

        if dataset.empty:
            raise ValueError(
                "Training dataset is empty."
            )

        dataset = dataset.sort_values("match_date")
        dataset.to_csv(OUTPUT_FILE, index=False)

        print("Training dataset created successfully.")
        print(f"Rows: {len(dataset)}")
        print(f"Columns: {len(dataset.columns)}")
        print(f"Saved at: {OUTPUT_FILE}")

        print("\nTarget distribution:")
        print(
            dataset["target"]
            .value_counts()
            .sort_index()
        )

        print("\nElo preview:")
        print(
            dataset[
                [
                    "home_team",
                    "away_team",
                    "home_elo",
                    "away_elo",
                    "elo_difference",
                ]
            ].head()
        )

        return dataset


if __name__ == "__main__":
    TrainingDatasetBuilder(
        last_n_matches=5
    ).build()