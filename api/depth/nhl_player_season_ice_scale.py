from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class NhlPlayerSeasonIceScale():
   player_id: int
   season_id: int
   multiplier: float
