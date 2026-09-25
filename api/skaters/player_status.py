from __future__ import annotations

from dataclasses import dataclass

from ..types import Types


@dataclass( frozen=True )
class PlayerStatus():
   player_id: int
   is_active: bool


   @classmethod
   def from_row( cls, row: Types.JsonObject | Types.Row ) -> PlayerStatus:
      return cls(
         player_id=int( row[ 'PLAYER_ID' ] ),
         is_active=bool( row[ 'IS_ACTIVE' ] ) )


   @classmethod
   def inactive_ids( cls, statuses: list[ PlayerStatus ] ) -> set[ int ]:
      return {
         status.player_id
         for status in statuses
         if not status.is_active
      }
