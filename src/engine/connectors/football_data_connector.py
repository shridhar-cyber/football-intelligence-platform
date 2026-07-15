from pathlib import Path
from typing import Dict, List
import hashlib

import pandas as pd


class FootballDataConnector:
    """
    Downloads and normalizes historical club match results from
    Football-Data.co.uk.

    Initial scope:
    - Premier League
    - Bundesliga
    - La Liga
    - Serie A
    - Ligue 1
    """

    name = "football-data"

    BASE_URL = "https://www.football-data.co.uk/mmz4281"

    LEAGUES: Dict[str, str] = {
        "E0": "Premier League",
        "D1": "Bundesliga",
        "SP1": "La Liga",
        "I1": "Serie A",
        "F1": "Ligue 1",
    }

    # 2015/16 through 2025/26
    SEASONS: List[str] = [
        "1516",
        "1617",
        "1718",
        "1819",
        "1920",
        "2021",
        "2122",
        "2223",
        "2324",
        "2425",
        "2526",
    ]

    REQUIRED_COLUMNS = [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",
    ]

    def __init__(self):
        self.raw_frames: List[pd.DataFrame] = []
        self.processed_data = pd.DataFrame()

        self.output_dir = Path("data/processed/football_data")
        self.output_file = self.output_dir / "matches.csv"

        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _season_name(season_code: str) -> str:
        start_year = int(season_code[:2])
        end_year = int(season_code[2:])

        start_year += 2000
        end_year += 2000

        return f"{start_year}/{end_year}"

    @staticmethod
    def _create_match_id(
        league_code: str,
        season_code: str,
        match_date: str,
        home_team: str,
        away_team: str,
    ) -> int:
        """
        Creates a stable negative integer ID so Football-Data records
        do not collide with positive StatsBomb match IDs.
        """
        raw_key = (
            f"{league_code}|{season_code}|{match_date}|"
            f"{home_team}|{away_team}"
        )

        digest = hashlib.sha256(
            raw_key.encode("utf-8")
        ).hexdigest()

        return -int(digest[:12], 16)

    def download(self) -> None:
        print("[Football-Data] Downloading league datasets...")

        self.raw_frames = []
        successful_files = 0
        skipped_files = 0

        for season_code in self.SEASONS:
            for league_code, league_name in self.LEAGUES.items():
                url = (
                    f"{self.BASE_URL}/"
                    f"{season_code}/"
                    f"{league_code}.csv"
                )

                try:
                    frame = pd.read_csv(url)

                    if frame.empty:
                        print(
                            f"Skipped empty file: "
                            f"{league_code} {season_code}"
                        )
                        skipped_files += 1
                        continue

                    frame["source_league_code"] = league_code
                    frame["source_league_name"] = league_name
                    frame["source_season_code"] = season_code
                    frame["source_url"] = url

                    self.raw_frames.append(frame)
                    successful_files += 1

                    print(
                        f"Downloaded: {league_name} "
                        f"{self._season_name(season_code)} "
                        f"({len(frame)} rows)"
                    )

                except Exception as exc:
                    skipped_files += 1
                    print(
                        f"Skipped: {league_code} {season_code} "
                        f"- {exc}"
                    )

        print(
            f"\nFootball-Data download complete. "
            f"Successful files: {successful_files}, "
            f"Skipped files: {skipped_files}"
        )

        if not self.raw_frames:
            raise RuntimeError(
                "Football-Data returned no usable datasets."
            )

    def validate(self) -> None:
        print("[Football-Data] Validating downloaded data...")

        valid_frames = []

        for frame in self.raw_frames:
            missing_columns = [
                column
                for column in self.REQUIRED_COLUMNS
                if column not in frame.columns
            ]

            if missing_columns:
                league = frame["source_league_code"].iloc[0]
                season = frame["source_season_code"].iloc[0]

                print(
                    f"Rejected {league} {season}: "
                    f"missing {missing_columns}"
                )
                continue

            valid_frames.append(frame)

        self.raw_frames = valid_frames

        if not self.raw_frames:
            raise ValueError(
                "No Football-Data files passed validation."
            )

        print(
            f"Validated datasets: {len(self.raw_frames)}"
        )

    def transform(self) -> None:
        print("[Football-Data] Transforming matches...")

        normalized_frames = []

        for frame in self.raw_frames:
            working = frame.copy()

            working["match_date"] = pd.to_datetime(
                working["Date"],
                format="mixed",
                dayfirst=True,
                errors="coerce",
            )

            working["home_score"] = pd.to_numeric(
                working["FTHG"],
                errors="coerce",
            )

            working["away_score"] = pd.to_numeric(
                working["FTAG"],
                errors="coerce",
            )

            working = working.dropna(
                subset=[
                    "match_date",
                    "HomeTeam",
                    "AwayTeam",
                    "home_score",
                    "away_score",
                ]
            )

            working["home_score"] = (
                working["home_score"].astype(int)
            )
            working["away_score"] = (
                working["away_score"].astype(int)
            )

            working["season_name"] = working[
                "source_season_code"
            ].apply(self._season_name)

            working["match_id"] = working.apply(
                lambda row: self._create_match_id(
                    league_code=row["source_league_code"],
                    season_code=row["source_season_code"],
                    match_date=row["match_date"].strftime(
                        "%Y-%m-%d"
                    ),
                    home_team=str(row["HomeTeam"]),
                    away_team=str(row["AwayTeam"]),
                ),
                axis=1,
            )

            normalized = pd.DataFrame({
                "match_id": working["match_id"],
                "competition_name":
                    working["source_league_name"],
                "season_name": working["season_name"],
                "match_date": working[
                    "match_date"
                ].dt.strftime("%Y-%m-%d"),
                "kick_off": (
                    working["Time"]
                    if "Time" in working.columns
                    else None
                ),
                "home_team": working["HomeTeam"],
                "away_team": working["AwayTeam"],
                "home_score": working["home_score"],
                "away_score": working["away_score"],
                "referee": (
                    working["Referee"]
                    if "Referee" in working.columns
                    else None
                ),
                "source": self.name,
                "source_league_code":
                    working["source_league_code"],
                "source_season_code":
                    working["source_season_code"],
            })

            normalized_frames.append(normalized)

        self.processed_data = pd.concat(
            normalized_frames,
            ignore_index=True,
        )

        self.processed_data = (
            self.processed_data
            .drop_duplicates(subset=["match_id"])
            .sort_values("match_date")
            .reset_index(drop=True)
        )

        print(
            f"Football-Data matches transformed: "
            f"{len(self.processed_data)}"
        )

    def save(self) -> None:
        print("[Football-Data] Saving processed data...")

        if self.processed_data.empty:
            raise ValueError(
                "No transformed Football-Data matches to save."
            )

        self.processed_data.to_csv(
            self.output_file,
            index=False,
        )

        print(f"Saved at: {self.output_file}")

    def sync(self) -> None:
        print(f"\n[{self.name}] Sync started")

        self.download()
        self.validate()
        self.transform()
        self.save()

        print(f"[{self.name}] Sync completed")