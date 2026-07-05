from src.warehouse.database import Database


class TeamRepository:

    def __init__(self):
        self.db = Database()
        self.conn = self.db.connect()

    def get_all_teams(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM teams
        ORDER BY team_name
        """)

        return cursor.fetchall()

    def get_team_by_name(self, team_name):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM teams
        WHERE LOWER(team_name)=LOWER(?)
        """, (team_name,))

        return cursor.fetchone()

    def count(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT COUNT(*)
        FROM teams
        """)

        return cursor.fetchone()[0]