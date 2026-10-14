from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class ProductionKeepSample():
   level: float
   latest_pace: float
   adjusted_following: float
   games: int
