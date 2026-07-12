from src.warehouse.database import Database


class MatchRepository:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.connect()

    def _rows_to_dicts(self, rows):
        columns = [
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
        ]

        return [dict(zip(columns, row)) for row in rows]

    def get_all_matches(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                match_id,
                competition_id,
                season_id,
                competition_name,
                season_name,
                match_date,
                kick_off,
                home_team_id,
                home_team,
                away_team_id,
                away_team,
                home_score,
                away_score,
                stadium,
                referee
            FROM matches
            ORDER BY match_date DESC
        """)

        return self._rows_to_dicts(cursor.fetchall())

    def get_matches_by_team(self, team_name):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                match_id,
                competition_id,
                season_id,
                competition_name,
                season_name,
                match_date,
                kick_off,
                home_team_id,
                home_team,
                away_team_id,
                away_team,
                home_score,
                away_score,
                stadium,
                referee
            FROM matches
            WHERE LOWER(home_team) = LOWER(?)
               OR LOWER(away_team) = LOWER(?)
            ORDER BY match_date DESC
        """, (team_name, team_name))

        return self._rows_to_dicts(cursor.fetchall())

    def get_last_n_matches_by_team(self, team_name, n=5):
        return self.get_matches_by_team(team_name)[:n]

    def get_head_to_head(self, team_one, team_two):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                match_id,
                competition_id,
                season_id,
                competition_name,
                season_name,
                match_date,
                kick_off,
                home_team_id,
                home_team,
                away_team_id,
                away_team,
                home_score,
                away_score,
                stadium,
                referee
            FROM matches
            WHERE (
                LOWER(home_team) = LOWER(?)
                AND LOWER(away_team) = LOWER(?)
            )
            OR (
                LOWER(home_team) = LOWER(?)
                AND LOWER(away_team) = LOWER(?)
            )
            ORDER BY match_date DESC
        """, (team_one, team_two, team_two, team_one))

        return self._rows_to_dicts(cursor.fetchall())

    def count(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM matches")
        return cursor.fetchone()[0]