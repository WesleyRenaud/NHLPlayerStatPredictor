from __future__ import annotations

from .player_status import PlayerStatus
from .types import Types


class PlayerStatusBuilder():
   @classmethod
   def build( cls, landing: Types.JsonObject ) -> PlayerStatus:
      return PlayerStatus(
         player_id=int( landing[ 'playerId' ] ),
         is_active=landing[ 'isActive' ] is True )


   @classmethod
   def build_all(
         cls,
         player_ids: list[ int ],
         landings: dict[ int, Types.JsonObject ] ) -> list[ PlayerStatus ]:
      return [
         cls.build( landings[ player_id ] )
         for player_id in player_ids
         if player_id in landings
      ]
