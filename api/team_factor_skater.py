from __future__ import annotations

from dataclasses import dataclass

from .types import Types


@dataclass( frozen=True )
class TeamFactorSkater():
   player_id: int
   contribution: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> TeamFactorSkater:
      return cls(
         player_id=int( row[ 'player_id' ] ),
         contribution=float( row[ 'contribution' ] ) )


   def to_dict( self ) -> dict[ str, int | float ]:
      return {
         'player_id': self.player_id,
         'contribution': self.contribution,
      }
