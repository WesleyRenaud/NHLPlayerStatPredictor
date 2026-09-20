from __future__ import annotations

from dataclasses import dataclass

from .types import Types


@dataclass( frozen=True )
class AgingFactor():
   age: int
   goals: float
   assists: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> AgingFactor:
      return cls(
         age=int( row[ 'age' ] ),
         goals=float( row[ 'goals' ] ),
         assists=float( row[ 'assists' ] ) )


   def to_dict( self ) -> dict[ str, int | float ]:
      return {
         'age': self.age,
         'goals': self.goals,
         'assists': self.assists,
      }
