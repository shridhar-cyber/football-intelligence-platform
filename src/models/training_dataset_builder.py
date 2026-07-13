from pathlib import Path

import pandas as pd

from src.repositories.match_repository import MatchRepository


OUTPUT_DIR = Path("data/features")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "training_dataset.csv"


class TrainingDatasetBuilder:
    """
    Generates leakage-free match-level training features.
    """

    def __init__(self, last_n_matches=5):
        self.match_repo = MatchRepository()
        self.last_n_matches = last_n_matches

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
                "win_rate": 0.0,
            }

        points = 0
        wins = 0
        goals_scored = 0
        goals_conceded = 0

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
            "win_rate": round(wins / total, 4),
        }

    @staticmethod
    def _target(home_score, away_score):
        if home_score > away_score:
            return 0  # Home win
        if home_score == away_score:
            return 1  # Draw
        return 2  # Away win

    def build(self):
        matches = self.match_repo.get_all_matches()

        rows = []

        for match in matches:
            if (
                match["match_date"] is None
                or match["home_score"] is None
                or match["away_score"] is None
            ):
                continue

            home_stats = self._team_statistics(
                match["home_team"],
                match["match_date"],
            )

            away_stats = self._team_statistics(
                match["away_team"],
                match["match_date"],
            )

            # Skip matches where neither team has prior history.
            if home_stats["form"] == 0 and away_stats["form"] == 0:
                continue

            rows.append({
                "match_id": match["match_id"],
                "match_date": match["match_date"],
                "home_team": match["home_team"],
                "away_team": match["away_team"],

                "home_form": home_stats["form"],
                "away_form": away_stats["form"],
                "form_difference": round(
                    home_stats["form"] - away_stats["form"],
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

                "home_win_rate": home_stats["win_rate"],
                "away_win_rate": away_stats["win_rate"],

                "target": self._target(
                    match["home_score"],
                    match["away_score"],
                ),
            })

        dataset = pd.DataFrame(rows)

        if dataset.empty:
            raise ValueError(
                "Training dataset is empty. "
                "More historical matches may be required."
            )

        dataset = dataset.sort_values("match_date")
        dataset.to_csv(OUTPUT_FILE, index=False)

        print("Training dataset created successfully.")
        print(f"Rows: {len(dataset)}")
        print(f"Columns: {len(dataset.columns)}")
        print(f"Saved at: {OUTPUT_FILE}")
        print("\nTarget distribution:")
        print(dataset["target"].value_counts().sort_index())

        return dataset


if __name__ == "__main__":
    builder = TrainingDatasetBuilder(last_n_matches=5)
    builder.build()