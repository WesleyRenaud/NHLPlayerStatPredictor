from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class ProductionSeason():
   age: int
   pace: float
   games: int
   arrival: float | None = None
