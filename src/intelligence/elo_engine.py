from collections import defaultdict

from src.repositories.match_repository import MatchRepository


INITIAL_ELO = 1500
K_FACTOR = 20
HOME_ADVANTAGE = 100


class EloEngine:

    def __init__(self):
        self.repository = MatchRepository()
        self.ratings = defaultdict(lambda: INITIAL_ELO)

    def expected_score(self, rating_a, rating_b, home_advantage=0):
        return 1 / (
            1 + 10 ** ((rating_b - (rating_a + home_advantage)) / 400)
        )

    def update_rating(self, rating, expected, actual):
        return rating + K_FACTOR * (actual - expected)

    def build(self):

        matches = self.repository.get_all_matches()

        matches = sorted(
            matches,
            key=lambda x: x["match_date"]
        )

        for match in matches:

            home = match["home_team"]
            away = match["away_team"]

            home_rating = self.ratings[home]
            away_rating = self.ratings[away]

            expected_home = self.expected_score(
                home_rating,
                away_rating,
                HOME_ADVANTAGE
            )

            expected_away = 1 - expected_home

            if match["home_score"] > match["away_score"]:
                actual_home = 1
                actual_away = 0

            elif match["home_score"] < match["away_score"]:
                actual_home = 0
                actual_away = 1

            else:
                actual_home = 0.5
                actual_away = 0.5

            self.ratings[home] = self.update_rating(
                home_rating,
                expected_home,
                actual_home
            )

            self.ratings[away] = self.update_rating(
                away_rating,
                expected_away,
                actual_away
            )

    def get_rating(self, team):

        if len(self.ratings) == 0:
            self.build()

        return round(self.ratings[team], 2)