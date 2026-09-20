from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class CareerPace():
   goals: float
   assists: float
