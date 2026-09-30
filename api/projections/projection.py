from __future__ import annotations

from dataclasses import dataclass

from ..time import Time

@dataclass( frozen=True )
class Projection():
   goals: int
   assists: int
   points: int
   games_played: int
   projected_toi: float | None = None


   def to_dict( self ) -> dict[ str, int | str | None ]:
      return {
         'goals': self.goals,
         'assists': self.assists,
         'points': self.points,
         'gamesPlayed': self.games_played,
         'projectedToi': (
            None if self.projected_toi is None
            else Time.clock_string( self.projected_toi ) ),
      }
