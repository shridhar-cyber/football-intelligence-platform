from src.intelligence.constants import K_FACTOR


class EloRatingSystem:

    @staticmethod
    def expected_score(rating_a, rating_b, home_advantage=0):
        return 1 / (
            1 + 10 ** ((rating_b - (rating_a + home_advantage)) / 400)
        )

    @staticmethod
    def update_rating(rating, expected, actual):
        return rating + K_FACTOR * (actual - expected)