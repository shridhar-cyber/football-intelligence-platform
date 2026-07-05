from src.warehouse.database import Database


class SeasonRepository:

    def __init__(self):
        self.db = Database()
        self.conn = self.db.connect()

    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM seasons
            ORDER BY competition_id, season_name
        """)
        return cursor.fetchall()

    def get_by_competition(self, competition_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM seasons
            WHERE competition_id = ?
            ORDER BY season_name
        """, (competition_id,))
        return cursor.fetchall()

    def count(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM seasons")
        return cursor.fetchone()[0]