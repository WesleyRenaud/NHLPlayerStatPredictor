from __future__ import annotations

from api.skaters.player_status import PlayerStatus


def Test_InactiveIds_TestInactive_ExpectPlayerId() -> None:
   player_id = 4
   statuses = [ PlayerStatus( player_id, False ), PlayerStatus( 1, True ) ]
   assert PlayerStatus.inactive_ids( statuses ) == { player_id }


def Test_InactiveIds_TestActive_ExpectEmpty() -> None:
   assert PlayerStatus.inactive_ids( [ PlayerStatus( 4, True ) ] ) == set()
