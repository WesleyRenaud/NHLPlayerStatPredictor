from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class SeasonPace():
   goals: float
   assists: float


   @classmethod
   def zero( cls ) -> SeasonPace:
      return cls( goals=0.0, assists=0.0 )
