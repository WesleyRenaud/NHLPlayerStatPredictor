from __future__ import annotations

from dataclasses import dataclass

from .scoring_paces import ScoringPaces

@dataclass( frozen=True )
class YearPace():
   scoring: ScoringPaces
   penalty_minutes: float | None
   games: int
   nhl_games: int
   shots: float | None = None
