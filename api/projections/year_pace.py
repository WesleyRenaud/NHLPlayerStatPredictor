from __future__ import annotations

from dataclasses import dataclass

from .pace_values import PaceValues

@dataclass( frozen=True )
class YearPace( PaceValues ):
   games: int
