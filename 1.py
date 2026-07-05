from src.repositories.competition_repository import CompetitionRepository
from src.repositories.season_repository import SeasonRepository

competition_repo = CompetitionRepository()
season_repo = SeasonRepository()

print("Competitions:", competition_repo.count())
print("Seasons:", season_repo.count())

print(competition_repo.get_by_id(9))
print(season_repo.get_by_competition(9))