from pathlib import Path
import sqlite3


DATABASE_DIR = Path("data/database")
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "football.db"


class Database:
    """
    Handles SQLite database connection.
    """

    def __init__(self):
        self.connection = None

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(DATABASE_PATH)

        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            