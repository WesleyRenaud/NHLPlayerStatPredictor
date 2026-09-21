from __future__ import annotations

from dataclasses import dataclass

from .skater_position import SkaterPosition
from .team import Team
from .types import Types


@dataclass( frozen=True )
class RosterSkater():
   player_id: int
   player_name: str
   position: SkaterPosition
   team: Team


   @classmethod
   def from_row( cls, row: Types.JsonObject | Types.Row ) -> RosterSkater:
      return cls(
         player_id=int( row[ 'PLAYER_ID' ] ),
         player_name=str( row[ 'PLAYER_NAME' ] ),
         position=SkaterPosition( str( row[ 'POSITION' ] ) ),
         team=Team( str( row[ 'TEAM' ] ) ) )
