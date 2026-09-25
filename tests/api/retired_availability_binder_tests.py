from __future__ import annotations

from api.player_status import PlayerStatus
from api.retired_availability_binder import RetiredAvailabilityBinder


def Test_Bind_TestInactive_ExpectZero() -> None:
   player_id = 4
   bound = RetiredAvailabilityBinder.bind(
      { player_id: 0.82, 1: 0.9 },
      [ PlayerStatus( player_id, False ) ] )
   assert bound[ player_id ] == 0.0
   assert bound[ 1 ] == 0.9


def Test_Bind_TestActive_ExpectUnchanged() -> None:
   share = 0.82
   player_id = 4
   bound = RetiredAvailabilityBinder.bind(
      { player_id: share },
      [ PlayerStatus( player_id, True ) ] )
   assert bound[ player_id ] == share
