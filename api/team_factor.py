from __future__ import annotations

from dataclasses import dataclass

from .team import Team
from .types import Types


@dataclass( frozen=True )
class TeamFactor():
   season: int
   team: Team
   rate: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> TeamFactor:
      return cls(
         season=int( row[ 'season' ] ),
         team=Team( str( row[ 'team' ] ) ),
         rate=float( row[ 'rate' ] ) )


   def to_dict( self ) -> dict[ str, int | float | str ]:
      return {
         'season': self.season,
         'team': self.team.value,
         'rate': self.rate,
      }


   @classmethod
   def rate(
         cls,
         factors: list[ TeamFactor ],
         season: int,
         team: Team ) -> float:
      for factor in factors:
         if factor.season == season and factor.team == team:
            return factor.rate
