from __future__ import annotations

from dataclasses import dataclass

from .types import Types


@dataclass( frozen=True )
class LeagueFactor():
   league: str
   goals: float
   assists: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> LeagueFactor:
      return cls(
         league=str( row[ 'league' ] ),
         goals=float( row[ 'goals' ] ),
         assists=float( row[ 'assists' ] ) )


   def to_dict( self ) -> dict[ str, str | float ]:
      return {
         'league': self.league,
         'goals': self.goals,
         'assists': self.assists,
      }
