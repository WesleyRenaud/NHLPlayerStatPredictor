from __future__ import annotations

from api.availability.retired_availability_binder import RetiredAvailabilityBinder
from api.skaters.player_status import PlayerStatus


def Test_Bind_TestInactive_ExpectZero() -> None:
   player_id = 4
   teammate_id = 1
   share = 0.82
   teammate_share = 0.9
   availabilities = { player_id: share, teammate_id: teammate_share }
   statuses = [ PlayerStatus( player_id, False ) ]

   bound = RetiredAvailabilityBinder.bind( availabilities, statuses )

   assert bound[ player_id ] == 0.0
   assert bound[ teammate_id ] == teammate_share


def Test_Bind_TestActive_ExpectUnchanged() -> None:
   share = 0.82
   player_id = 4
   availabilities = { player_id: share }
   statuses = [ PlayerStatus( player_id, True ) ]

   bound = RetiredAvailabilityBinder.bind( availabilities, statuses )

   assert bound[ player_id ] == share
