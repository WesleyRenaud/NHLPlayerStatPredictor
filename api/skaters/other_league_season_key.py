from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class OtherLeagueSeasonKey():
   player_id: int
   season_id: int
   league: str
