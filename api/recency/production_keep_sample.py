from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class ProductionKeepSample():
   relative_slope: float
   level: float
   latest_pace: float
   adjusted_following: float
   games: int
