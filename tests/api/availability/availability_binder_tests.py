from __future__ import annotations

from api.availability.availability_binder import AvailabilityBinder
from api.depth.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


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
   first_share = 0.5
   second_share = 0.25
   lower_implied = 16.0
   higher_implied = 24.0
   lower = _skater( 2, lower_implied, 0.9 )
   higher = _skater( 1, higher_implied, 0.9 )
   skaters = [ lower, higher ]
   shares = [ first_share, second_share ]

   bound = AvailabilityBinder.bind( skaters, shares )

   by_id = { skater.player_id: skater.availability for skater in bound }
   assert by_id[ higher.player_id ] == first_share
   assert by_id[ lower.player_id ] == second_share
   assert [ skater.player_id for skater in bound ] == [
      lower.player_id,
      higher.player_id,
   ]
