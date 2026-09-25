from __future__ import annotations

from api.skaters.player_status import PlayerStatus
from api.skaters.player_status_builder import PlayerStatusBuilder


def Test_Build_TestActiveLanding_ExpectTrue() -> None:
   status = PlayerStatusBuilder.build( { 'playerId': 7, 'isActive': True } )
   assert status == PlayerStatus( 7, True )


def Test_Build_TestInactiveLanding_ExpectFalse() -> None:
   status = PlayerStatusBuilder.build( { 'playerId': 7, 'isActive': False } )
   assert status == PlayerStatus( 7, False )


def Test_BuildAll_TestMissingLanding_ExpectSkipped() -> None:
   first_id = 7
   second_id = 8
   landing = { 'playerId': second_id, 'isActive': True }
   assert PlayerStatusBuilder.build_all(
      [ first_id, second_id ],
      { second_id: landing } ) == [ PlayerStatus( second_id, True ) ]
