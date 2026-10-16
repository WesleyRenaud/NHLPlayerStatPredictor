from __future__ import annotations

from dataclasses import dataclass

from ..types import Types


@dataclass( frozen=True )
class CurrentSeasonWeight():
   season_share: float
   weight: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> CurrentSeasonWeight:
      return cls( float( row[ 'season_share' ] ), float( row[ 'weight' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'season_share': self.season_share,
         'weight': self.weight,
      }
