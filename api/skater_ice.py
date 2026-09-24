from __future__ import annotations

from dataclasses import dataclass

from .types import Types


@dataclass( frozen=True )
class SkaterIce():
   player_id: int
   last_toi: float | None
   projected_toi: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> SkaterIce:
      last_toi = row[ 'last_toi' ]
      return cls(
         int( row[ 'player_id' ] ),
         None if last_toi is None else float( last_toi ),
         float( row[ 'projected_toi' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'player_id': self.player_id,
         'last_toi': None if self.last_toi is None else round( self.last_toi, 2 ),
         'projected_toi': round( self.projected_toi, 2 ),
      }
