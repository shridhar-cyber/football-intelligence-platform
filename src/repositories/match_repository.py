from src.warehouse.database import Database


class MatchRepository:

    def __init__(self):
        self.db = Database()
        self.conn = self.db.connect()

    def get_all_matches(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM matches
        """)

        return cursor.fetchall()

    def count(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT COUNT(*)
        FROM matches
        """)

        return cursor.fetchone()[0]