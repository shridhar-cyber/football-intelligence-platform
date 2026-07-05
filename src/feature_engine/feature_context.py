from dataclasses import dataclass
from typing import Optional


@dataclass
class FeatureContext:
    home_team: str
    away_team: str
    match_date: Optional[str] = None
    competition_name: Optional[str] = None
    last_n_matches: int = 5