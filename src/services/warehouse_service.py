from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from src.warehouse.database import Database
from src.warehouse.schema import WarehouseSchema


WAREHOUSE_DIR = Path("data/warehouse")

UNIFIED_MATCHES_FILE = Path(
    "data/processed/unified/matches.csv"
)


TABLE_COLUMNS = {
    "competitions": [
        "competition_id",
        "competition_name",
        "country_name",
    ],
    "seasons": [
        "season_id",
        "competition_id",
        "season_name",
    ],
    "teams": [
        "team_id",
        "team_name",
        "source",
        "source_team_id",
    ],
    "matches": [
        "match_id",
        "competition_id",
        "season_id",
        "competition_name",
        "season_name",
        "match_date",
        "kick_off",
        "home_team_id",
        "home_team",
        "away_team_id",
        "away_team",
        "home_score",
        "away_score",
        "stadium",
        "referee",
    ],
}


LEAGUE_COUNTRIES = {
    "Premier League": "England",
    "Bundesliga": "Germany",
    "La Liga": "Spain",
    "Serie A": "Italy",
    "Ligue 1": "France",
}


class WarehouseService:
    """
    Prepares and loads the unified football warehouse.

    Responsibilities:
    - Read the unified multi-source match registry.
    - Resolve competition IDs.
    - Resolve season IDs.
    - Resolve or generate string-based team IDs.
    - Produce warehouse-ready CSV files.
    - Rebuild and verify the SQLite warehouse.
    """

    def __init__(self):
        WAREHOUSE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.db = Database()
        self.conn = self.db.connect()

    @staticmethod
    def _normalize_name(value) -> str:
        """
        Normalize names for reliable lookup matching.
        """
        if pd.isna(value):
            return ""

        return " ".join(
            str(value)
            .strip()
            .lower()
            .split()
        )

    @staticmethod
    def _next_numeric_id(
        dataframe: pd.DataFrame,
        column: str,
    ) -> int:
        """
        Return the next available numeric ID.
        """
        if (
            dataframe.empty
            or column not in dataframe.columns
        ):
            return 1

        values = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        ).dropna()

        if values.empty:
            return 1

        return int(values.max()) + 1

    @staticmethod
    def _next_team_number(
        teams: pd.DataFrame,
    ) -> int:
        """
        Find the next numeric suffix for IDs such as:

        FI_TEAM_000001
        FI_TEAM_000002
        """
        if (
            teams.empty
            or "team_id" not in teams.columns
        ):
            return 1

        numeric_parts = (
            teams["team_id"]
            .astype(str)
            .str.extract(r"(\d+)$")[0]
        )

        numeric_parts = pd.to_numeric(
            numeric_parts,
            errors="coerce",
        ).dropna()

        if numeric_parts.empty:
            return 1

        return int(numeric_parts.max()) + 1

    @staticmethod
    def _load_csv(
        path: Path,
        required_columns: List[str],
    ) -> pd.DataFrame:
        """
        Read a warehouse CSV and guarantee its expected columns.
        """
        if not path.exists():
            return pd.DataFrame(
                columns=required_columns
            )

        dataframe = pd.read_csv(
            path,
            dtype={
                "team_id": str,
                "source_team_id": str,
            },
        )

        for column in required_columns:
            if column not in dataframe.columns:
                dataframe[column] = None

        return dataframe[required_columns]

    def initialize(self) -> None:
        print(
            "\nInitializing Football Warehouse...\n"
        )

        WarehouseSchema().create_tables()

        print("Schema initialized.\n")

    def _resolve_competitions(
        self,
        competitions: pd.DataFrame,
        matches: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        competition_lookup: Dict[str, int] = {}

        for _, row in competitions.iterrows():
            normalized_name = self._normalize_name(
                row["competition_name"]
            )

            competition_id = pd.to_numeric(
                row["competition_id"],
                errors="coerce",
            )

            if (
                normalized_name
                and not pd.isna(competition_id)
            ):
                competition_lookup[
                    normalized_name
                ] = int(competition_id)

        next_competition_id = (
            self._next_numeric_id(
                competitions,
                "competition_id",
            )
        )

        new_rows = []

        competition_names = (
            matches["competition_name"]
            .dropna()
            .astype(str)
            .unique()
        )

        for competition_name in competition_names:
            normalized_name = self._normalize_name(
                competition_name
            )

            if normalized_name in competition_lookup:
                continue

            competition_id = next_competition_id
            next_competition_id += 1

            competition_lookup[
                normalized_name
            ] = competition_id

            new_rows.append(
                {
                    "competition_id": competition_id,
                    "competition_name": competition_name,
                    "country_name": (
                        LEAGUE_COUNTRIES.get(
                            competition_name,
                            "International",
                        )
                    ),
                }
            )

        if new_rows:
            competitions = pd.concat(
                [
                    competitions,
                    pd.DataFrame(new_rows),
                ],
                ignore_index=True,
            )

        matches["competition_id"] = (
            matches["competition_name"].apply(
                lambda name: competition_lookup.get(
                    self._normalize_name(name)
                )
            )
        )

        return competitions, matches

    def _resolve_seasons(
        self,
        seasons: pd.DataFrame,
        matches: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        season_lookup: Dict[
            Tuple[int, str],
            int,
        ] = {}

        for _, row in seasons.iterrows():
            competition_id = pd.to_numeric(
                row["competition_id"],
                errors="coerce",
            )

            season_id = pd.to_numeric(
                row["season_id"],
                errors="coerce",
            )

            season_name = self._normalize_name(
                row["season_name"]
            )

            if (
                pd.isna(competition_id)
                or pd.isna(season_id)
                or not season_name
            ):
                continue

            key = (
                int(competition_id),
                season_name,
            )

            season_lookup[key] = int(season_id)

        next_season_id = self._next_numeric_id(
            seasons,
            "season_id",
        )

        new_rows = []

        unique_seasons = (
            matches[
                [
                    "competition_id",
                    "season_name",
                ]
            ]
            .dropna()
            .drop_duplicates()
        )

        for _, row in unique_seasons.iterrows():
            competition_id = int(
                row["competition_id"]
            )

            season_name = str(
                row["season_name"]
            )

            key = (
                competition_id,
                self._normalize_name(season_name),
            )

            if key in season_lookup:
                continue

            season_id = next_season_id
            next_season_id += 1

            season_lookup[key] = season_id

            new_rows.append(
                {
                    "season_id": season_id,
                    "competition_id": competition_id,
                    "season_name": season_name,
                }
            )

        if new_rows:
            seasons = pd.concat(
                [
                    seasons,
                    pd.DataFrame(new_rows),
                ],
                ignore_index=True,
            )

        def resolve_season_id(row):
            if pd.isna(row["competition_id"]):
                return None

            key = (
                int(row["competition_id"]),
                self._normalize_name(
                    row["season_name"]
                ),
            )

            return season_lookup.get(key)

        matches["season_id"] = matches.apply(
            resolve_season_id,
            axis=1,
        )

        return seasons, matches

    def _resolve_teams(
        self,
        teams: pd.DataFrame,
        matches: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        team_lookup: Dict[str, str] = {}

        for _, row in teams.iterrows():
            normalized_name = self._normalize_name(
                row["team_name"]
            )

            team_id = str(
                row["team_id"]
            ).strip()

            if (
                normalized_name
                and team_id
                and team_id.lower() != "nan"
            ):
                team_lookup[
                    normalized_name
                ] = team_id

        next_team_number = self._next_team_number(
            teams
        )

        all_team_names = pd.concat(
            [
                matches["home_team"],
                matches["away_team"],
            ],
            ignore_index=True,
        )

        all_team_names = (
            all_team_names
            .dropna()
            .astype(str)
            .unique()
        )

        new_rows = []

        for team_name in all_team_names:
            normalized_name = self._normalize_name(
                team_name
            )

            if normalized_name in team_lookup:
                continue

            team_id = (
                f"FI_TEAM_{next_team_number:06d}"
            )
            next_team_number += 1

            team_lookup[
                normalized_name
            ] = team_id

            matching_sources = matches.loc[
                (
                    matches["home_team"]
                    .astype(str)
                    .apply(self._normalize_name)
                    == normalized_name
                )
                |
                (
                    matches["away_team"]
                    .astype(str)
                    .apply(self._normalize_name)
                    == normalized_name
                ),
                "source",
            ] if "source" in matches.columns else pd.Series(
                dtype=str
            )

            source = (
                str(matching_sources.dropna().iloc[0])
                if not matching_sources.dropna().empty
                else "football-data"
            )

            new_rows.append(
                {
                    "team_id": team_id,
                    "team_name": team_name,
                    "source": source,
                    "source_team_id": None,
                }
            )

        if new_rows:
            teams = pd.concat(
                [
                    teams,
                    pd.DataFrame(new_rows),
                ],
                ignore_index=True,
            )

        matches["home_team_id"] = (
            matches["home_team"].apply(
                lambda name: team_lookup.get(
                    self._normalize_name(name)
                )
            )
        )

        matches["away_team_id"] = (
            matches["away_team"].apply(
                lambda name: team_lookup.get(
                    self._normalize_name(name)
                )
            )
        )

        return teams, matches

    @staticmethod
    def _validate_relationships(
        matches: pd.DataFrame,
    ) -> None:
        relationship_columns = [
            "competition_id",
            "season_id",
            "home_team_id",
            "away_team_id",
        ]

        unresolved = matches[
            relationship_columns
        ].isnull().sum()

        if unresolved.sum() > 0:
            raise ValueError(
                "Unresolved warehouse relationships:\n"
                f"{unresolved}"
            )

    @staticmethod
    def _convert_numeric_columns(
        competitions: pd.DataFrame,
        seasons: pd.DataFrame,
        matches: pd.DataFrame,
    ) -> Tuple[
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
    ]:
        competition_numeric_columns = [
            "competition_id",
        ]

        season_numeric_columns = [
            "season_id",
            "competition_id",
        ]

        match_numeric_columns = [
            "match_id",
            "competition_id",
            "season_id",
            "home_score",
            "away_score",
        ]

        for column in competition_numeric_columns:
            competitions[column] = pd.to_numeric(
                competitions[column],
                errors="raise",
            ).astype("int64")

        for column in season_numeric_columns:
            seasons[column] = pd.to_numeric(
                seasons[column],
                errors="raise",
            ).astype("int64")

        for column in match_numeric_columns:
            matches[column] = pd.to_numeric(
                matches[column],
                errors="raise",
            ).astype("int64")

        # Team IDs remain strings.
        matches["home_team_id"] = (
            matches["home_team_id"].astype(str)
        )

        matches["away_team_id"] = (
            matches["away_team_id"].astype(str)
        )

        return competitions, seasons, matches

    def prepare_unified_warehouse_files(
        self,
    ) -> None:
        print(
            "Preparing unified warehouse files...\n"
        )

        if not UNIFIED_MATCHES_FILE.exists():
            print(
                "Unified match registry not found. "
                "Using existing warehouse CSV files."
            )
            return

        competitions_path = (
            WAREHOUSE_DIR / "competitions.csv"
        )

        seasons_path = (
            WAREHOUSE_DIR / "seasons.csv"
        )

        teams_path = (
            WAREHOUSE_DIR / "teams.csv"
        )

        matches_path = (
            WAREHOUSE_DIR / "matches.csv"
        )

        competitions = self._load_csv(
            competitions_path,
            TABLE_COLUMNS["competitions"],
        )

        seasons = self._load_csv(
            seasons_path,
            TABLE_COLUMNS["seasons"],
        )

        teams = self._load_csv(
            teams_path,
            TABLE_COLUMNS["teams"],
        )

        matches = pd.read_csv(
            UNIFIED_MATCHES_FILE,
            dtype={
                "home_team_id": str,
                "away_team_id": str,
            },
        )

        for column in TABLE_COLUMNS["matches"]:
            if column not in matches.columns:
                matches[column] = None

        competitions, matches = (
            self._resolve_competitions(
                competitions,
                matches,
            )
        )

        seasons, matches = (
            self._resolve_seasons(
                seasons,
                matches,
            )
        )

        teams, matches = self._resolve_teams(
            teams,
            matches,
        )

        self._validate_relationships(matches)

        competitions, seasons, matches = (
            self._convert_numeric_columns(
                competitions,
                seasons,
                matches,
            )
        )

        teams["team_id"] = (
            teams["team_id"].astype(str)
        )

        teams["team_name"] = (
            teams["team_name"].astype(str)
        )

        competitions = (
            competitions
            .drop_duplicates(
                subset=["competition_id"],
                keep="last",
            )
            .sort_values("competition_id")
            .reset_index(drop=True)
        )

        seasons = (
            seasons
            .drop_duplicates(
                subset=[
                    "competition_id",
                    "season_name",
                ],
                keep="last",
            )
            .sort_values(
                [
                    "competition_id",
                    "season_name",
                ]
            )
            .reset_index(drop=True)
        )

        teams = (
            teams
            .drop_duplicates(
                subset=["team_id"],
                keep="last",
            )
            .sort_values("team_id")
            .reset_index(drop=True)
        )

        matches = (
            matches
            .drop_duplicates(
                subset=["match_id"],
                keep="last",
            )
            .sort_values(
                [
                    "match_date",
                    "match_id",
                ]
            )
            .reset_index(drop=True)
        )

        competitions[
            TABLE_COLUMNS["competitions"]
        ].to_csv(
            competitions_path,
            index=False,
        )

        seasons[
            TABLE_COLUMNS["seasons"]
        ].to_csv(
            seasons_path,
            index=False,
        )

        teams[
            TABLE_COLUMNS["teams"]
        ].to_csv(
            teams_path,
            index=False,
        )

        matches[
            TABLE_COLUMNS["matches"]
        ].to_csv(
            matches_path,
            index=False,
        )

        print(
            f"Competitions prepared: "
            f"{len(competitions)}"
        )

        print(
            f"Seasons prepared: "
            f"{len(seasons)}"
        )

        print(
            f"Teams prepared: "
            f"{len(teams)}"
        )

        print(
            f"Matches prepared: "
            f"{len(matches)}"
        )

        print(
            "\nUnified warehouse files prepared.\n"
        )

    def clear_tables(self) -> None:
        """
        Clear child tables before parent tables.
        """
        cursor = self.conn.cursor()

        cursor.execute(
            "DELETE FROM matches"
        )

        cursor.execute(
            "DELETE FROM seasons"
        )

        cursor.execute(
            "DELETE FROM teams"
        )

        cursor.execute(
            "DELETE FROM competitions"
        )

        self.conn.commit()

    def load_table(
        self,
        csv_file: str,
        table_name: str,
    ) -> None:
        csv_path = WAREHOUSE_DIR / csv_file

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Warehouse file not found: "
                f"{csv_path}"
            )

        dtype_mapping = {}

        if table_name == "teams":
            dtype_mapping = {
                "team_id": str,
                "source_team_id": str,
            }

        if table_name == "matches":
            dtype_mapping = {
                "home_team_id": str,
                "away_team_id": str,
            }

        dataframe = pd.read_csv(
            csv_path,
            dtype=dtype_mapping,
        )

        required_columns = (
            TABLE_COLUMNS[table_name]
        )

        missing_columns = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                f"{csv_file} is missing columns: "
                f"{missing_columns}"
            )

        dataframe = dataframe[
            required_columns
        ]

        dataframe.to_sql(
            table_name,
            self.conn,
            if_exists="append",
            index=False,
        )

        self.conn.commit()

        print(
            f"{table_name:<15} "
            f"Loaded ({len(dataframe)} rows)"
        )

    def load(self) -> None:
        print(
            "Loading warehouse tables...\n"
        )

        self.clear_tables()

        self.load_table(
            "competitions.csv",
            "competitions",
        )

        self.load_table(
            "seasons.csv",
            "seasons",
        )

        self.load_table(
            "teams.csv",
            "teams",
        )

        self.load_table(
            "matches.csv",
            "matches",
        )

        print(
            "\nAll warehouse tables loaded."
        )

    def verify(self) -> None:
        print(
            "\nVerifying Warehouse...\n"
        )

        cursor = self.conn.cursor()

        for table in TABLE_COLUMNS:
            cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            count = cursor.fetchone()[0]

            print(
                f"{table:<15} {count} rows"
            )

        cursor.execute(
            """
            SELECT source, COUNT(*)
            FROM teams
            GROUP BY source
            ORDER BY COUNT(*) DESC
            """
        )

        print(
            "\nTeam source distribution:"
        )

        for source, count in cursor.fetchall():
            print(
                f"{str(source):<15} {count}"
            )

        print(
            "\nVerification complete."
        )

    def run(self) -> None:
        self.initialize()
        self.prepare_unified_warehouse_files()
        self.load()
        self.verify()


if __name__ == "__main__":
    WarehouseService().run()