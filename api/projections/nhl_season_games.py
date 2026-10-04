from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class NhlSeasonGames():
   season_id: int
   games_played: int
