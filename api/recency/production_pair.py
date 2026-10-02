from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class ProductionPair():
   from_age: int
   to_age: int
   prior_pace: float
   following_pace: float
   games: float
