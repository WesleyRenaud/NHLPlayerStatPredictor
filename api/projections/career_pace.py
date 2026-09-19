from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class CareerPace():
   goals: int
   assists: int
   points: int
