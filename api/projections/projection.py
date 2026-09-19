from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class Projection():
   goals: int
   assists: int
   points: int


   def to_dict( self ) -> dict[ str, int ]:
      return {
         'goals': self.goals,
         'assists': self.assists,
         'points': self.points,
      }
