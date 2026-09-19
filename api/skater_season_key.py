from __future__ import annotations

from dataclasses import dataclass

from .types import Types


@dataclass( frozen=True )
class SkaterSeasonKey():
   player_id: int
   season_id: int


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> SkaterSeasonKey:
      return cls( int( row[ 'PLAYER_ID' ] ), int( row[ 'SEASON_ID' ] ) )
