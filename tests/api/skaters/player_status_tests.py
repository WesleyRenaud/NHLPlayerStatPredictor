from __future__ import annotations

from api.skaters.player_status import PlayerStatus


def Test_InactiveIds_TestInactive_ExpectPlayerId() -> None:
   inactive_id = 4
   active_id = 1
   statuses = [
      PlayerStatus( inactive_id, False ),
      PlayerStatus( active_id, True ),
   ]

   inactive = PlayerStatus.inactive_ids( statuses )

   assert inactive == { inactive_id }


def Test_InactiveIds_TestActive_ExpectEmpty() -> None:
   player_id = 4
   statuses = [ PlayerStatus( player_id, True ) ]

   inactive = PlayerStatus.inactive_ids( statuses )

   assert inactive == set()
