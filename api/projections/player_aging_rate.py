from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class PlayerAgingRate():
   pair_count: int
   goals: float
   assists: float
