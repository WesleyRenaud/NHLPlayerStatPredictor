from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class SkaterGame():
   game_number: int
   points: int
