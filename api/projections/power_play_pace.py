from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class PowerPlayPace():
   goals: float
   assists: float


   @classmethod
   def zero( cls ) -> PowerPlayPace:
      return cls( goals=0.0, assists=0.0 )