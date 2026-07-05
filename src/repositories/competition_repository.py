from src.warehouse.database import Database


class CompetitionRepository:

    def __init__(self):
        self.db = Database()
        self.conn = self.db.connect()

    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM competitions
            ORDER BY competition_name
        """)
        return cursor.fetchall()

    def get_by_id(self, competition_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM competitions
            WHERE competition_id = ?
        """, (competition_id,))
        return cursor.fetchone()

    def count(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM competitions")
        return cursor.fetchone()[0]
    