from __future__ import annotations

from api.skaters.player_status import PlayerStatus
from api.skaters.player_status_builder import PlayerStatusBuilder


def Test_Build_TestActiveLanding_ExpectTrue() -> None:
   player_id = 7
   is_active = True
   landing = { 'playerId': player_id, 'isActive': is_active }

   status = PlayerStatusBuilder.build( landing )

   assert status == PlayerStatus( player_id, is_active )


def Test_Build_TestInactiveLanding_ExpectFalse() -> None:
   player_id = 7
   is_active = False
   landing = { 'playerId': player_id, 'isActive': is_active }

   status = PlayerStatusBuilder.build( landing )

   assert status == PlayerStatus( player_id, is_active )


def Test_BuildAll_TestMissingLanding_ExpectSkipped() -> None:
   first_id = 7
   second_id = 8
   is_active = True
   landing = { 'playerId': second_id, 'isActive': is_active }
   player_ids = [ first_id, second_id ]
   landings = { second_id: landing }

   statuses = PlayerStatusBuilder.build_all( player_ids, landings )

   assert statuses == [ PlayerStatus( second_id, is_active ) ]
