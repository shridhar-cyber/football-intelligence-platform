import pandas as pd
from pathlib import Path

from src.repositories.match_repository import MatchRepository


FEATURE_DIR = Path("data/features")
FEATURE_DIR.mkdir(parents=True, exist_ok=True)


class TeamFormService:
    """
    Builds basic team form features from match results.
    """

    def __init__(self):
        self.match_repo = MatchRepository()

    def build_team_form(self):
        matches = self.match_repo.get_all_matches()

        columns = [
            "match_id", "competition_id", "season_id",
            "competition_name", "season_name",
            "match_date", "kick_off",
            "home_team_id", "home_team",
            "away_team_id", "away_team",
            "home_score", "away_score",
            "stadium", "referee"
        ]

        matches_df = pd.DataFrame(matches, columns=columns)

        team_rows = []

        for _, row in matches_df.iterrows():
            home_result = self._get_result(row["home_score"], row["away_score"])
            away_result = self._get_result(row["away_score"], row["home_score"])

            team_rows.append({
                "team_id": row["home_team_id"],
                "team_name": row["home_team"],
                "match_id": row["match_id"],
                "match_date": row["match_date"],
                "goals_scored": row["home_score"],
                "goals_conceded": row["away_score"],
                "result": home_result
            })

            team_rows.append({
                "team_id": row["away_team_id"],
                "team_name": row["away_team"],
                "match_id": row["match_id"],
                "match_date": row["match_date"],
                "goals_scored": row["away_score"],
                "goals_conceded": row["home_score"],
                "result": away_result
            })

        team_match_df = pd.DataFrame(team_rows)

        form_df = (
            team_match_df
            .groupby(["team_id", "team_name"])
            .agg(
                matches_played=("match_id", "count"),
                wins=("result", lambda x: (x == "W").sum()),
                draws=("result", lambda x: (x == "D").sum()),
                losses=("result", lambda x: (x == "L").sum()),
                goals_scored=("goals_scored", "sum"),
                goals_conceded=("goals_conceded", "sum"),
            )
            .reset_index()
        )

        form_df["form_score"] = (
            (form_df["wins"] * 3 + form_df["draws"]) /
            (form_df["matches_played"] * 3)
        ).round(3)

        output_path = FEATURE_DIR / "team_form.csv"
        form_df.to_csv(output_path, index=False)

        print("Team form features created.")
        print(f"Saved at: {output_path}")
        print(form_df.head())

        return form_df

    def _get_result(self, goals_for, goals_against):
        if goals_for > goals_against:
            return "W"
        elif goals_for == goals_against:
            return "D"
        return "L"


if __name__ == "__main__":
    service = TeamFormService()
    service.build_team_form()