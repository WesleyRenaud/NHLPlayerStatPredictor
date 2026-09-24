from __future__ import annotations

from api.availability_binder import AvailabilityBinder
from api.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _skater( player_id: int, implied: float, availability: float ) -> IceSkater:
   return IceSkater(
      player_id,
      str( player_id ),
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      implied,
      implied,
      availability )


def Test_Bind_TestImpliedOrder_ExpectSharesOnRanks() -> None:
   bound = AvailabilityBinder.bind(
      [ _skater( 2, 16.0, 0.9 ), _skater( 1, 24.0, 0.9 ) ],
      [ 0.5, 0.25 ] )
   by_id = { skater.player_id: skater.availability for skater in bound }
   assert by_id[ 1 ] == 0.5
   assert by_id[ 2 ] == 0.25
   assert [ skater.player_id for skater in bound ] == [ 2, 1 ]
