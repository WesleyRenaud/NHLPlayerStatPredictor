from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class ShortHandedPace():
   goals: float
   assists: float