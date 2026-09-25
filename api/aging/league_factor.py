from __future__ import annotations

from dataclasses import dataclass

from ..types import Types


@dataclass( frozen=True )
class LeagueFactor():
   league: str
   rate: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> LeagueFactor:
      return cls( league=str( row[ 'league' ] ), rate=float( row[ 'rate' ] ) )


   def to_dict( self ) -> dict[ str, str | float ]:
      return {
         'league': self.league,
         'rate': self.rate,
      }


   @classmethod
   def rate(
         cls,
         factors: list[ LeagueFactor ],
         league: str ) -> float | None:
      for factor in factors:
         if factor.league == league:
            return factor.rate

      return None
