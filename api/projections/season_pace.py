from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class SeasonPace():
   goals: float
   assists: float
