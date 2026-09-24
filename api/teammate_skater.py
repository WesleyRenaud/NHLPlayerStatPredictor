from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class TeammateSkater():
   player_id: int
   contribution: float
   availability: float
   prior_availability: float | None
