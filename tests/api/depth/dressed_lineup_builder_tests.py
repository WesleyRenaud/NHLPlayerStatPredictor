from __future__ import annotations

from api.depth.depth_group import DepthGroup
from api.depth.dressed_lineup_builder import DressedLineupBuilder
from api.depth.ice_skater import IceSkater
from api.depth.slot_average import SlotAverage
from api.depth.slot_filler import SlotFiller
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _skater( player_id: int, implied: float ) -> IceSkater:
   return IceSkater(
      player_id,
      str( player_id ),
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      implied,
      implied,
      1.0 )


def Test_Build_TestTwoMissing_ExpectExtraThenReplacement() -> None:
   implied = 20.0
   extra_implied = 16.0
   present = [ _skater( index, implied ) for index in range( 1, 5 ) ]
   extra = _skater( 7, extra_implied )

   lineup = DressedLineupBuilder.build(
      present,
      [ extra ],
      [],
      DepthGroup.defense() )

   assert abs(
      lineup.implied - ( implied * len( present ) + extra_implied ) ) < 0.001


def Test_Build_TestFullSix_ExpectNoFill() -> None:
   implied = 20.0
   present = [ _skater( index, implied ) for index in range( 1, 7 ) ]

   lineup = DressedLineupBuilder.build(
      present,
      [ _skater( 7, 16.0 ) ],
      [],
      DepthGroup.defense() )

   assert abs( lineup.implied - implied * len( present ) ) < 0.001


def Test_Build_TestTwoMissing_ExpectExtraThenSlotEight() -> None:
   implied = 20.0
   extra_implied = 16.0
   present = [ _skater( index, implied ) for index in range( 1, 5 ) ]
   slots = [ SlotAverage( 8, 13.0, 1.0, 10.0 ) ]
   extra = _skater( 7, extra_implied )

   lineup = DressedLineupBuilder.build(
      present,
      [ extra ],
      slots,
      DepthGroup.defense() )

   eighth = SlotFiller.implied( slots, slots[ Position.FIRST ].slot )
   assert abs(
      lineup.implied - ( implied * len( present ) + extra_implied + eighth ) ) < 0.001
