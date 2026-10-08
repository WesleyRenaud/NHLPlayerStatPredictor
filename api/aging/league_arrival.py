from __future__ import annotations

from dataclasses import dataclass

from ..types import Types


@dataclass( frozen=True )
class LeagueArrival():
   league: str
   age: int
   rate: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> LeagueArrival:
      return cls(
         league=str( row[ 'league' ] ),
         age=int( row[ 'age' ] ),
         rate=float( row[ 'rate' ] ) )


   def to_dict( self ) -> dict[ str, str | int | float ]:
      return {
         'league': self.league,
         'age': self.age,
         'rate': self.rate,
      }


   @classmethod
   def rate(
         cls,
         arrivals: list[ LeagueArrival ],
         league: str,
         age: int ) -> float | None:
      for arrival in arrivals:
         if arrival.league == league and arrival.age == age:
            return arrival.rate

      return None
