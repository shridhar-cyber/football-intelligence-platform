from src.intelligence.elo_engine import EloEngine


class EloRepository:

    def __init__(self):
        self.engine = EloEngine()

    def get_team_rating(self, team_name):
        return self.engine.get_rating(team_name)