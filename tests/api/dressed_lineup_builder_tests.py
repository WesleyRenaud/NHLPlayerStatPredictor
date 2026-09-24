from __future__ import annotations

from api.depth_group import DepthGroup
from api.dressed_lineup_builder import DressedLineupBuilder
from api.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.slot_average import SlotAverage
from api.slot_filler import SlotFiller
from api.team import Team


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
   present = [ _skater( index, 20.0 ) for index in range( 1, 5 ) ]
   lineup = DressedLineupBuilder.build(
      present,
      [ _skater( 7, 16.0 ) ],
      [],
      DepthGroup.defense() )
   assert abs(
      lineup.implied - ( 80.0 + 16.0 ) ) < 0.001


def Test_Build_TestFullSix_ExpectNoFill() -> None:
   present = [ _skater( index, 20.0 ) for index in range( 1, 7 ) ]
   lineup = DressedLineupBuilder.build(
      present,
      [ _skater( 7, 16.0 ) ],
      [],
      DepthGroup.defense() )
   assert abs( lineup.implied - 120.0 ) < 0.001


def Test_Build_TestTwoMissing_ExpectExtraThenSlotEight() -> None:
   present = [ _skater( index, 20.0 ) for index in range( 1, 5 ) ]
   slots = [ SlotAverage( 8, 13.0, 1.0, 10.0 ) ]
   lineup = DressedLineupBuilder.build(
      present,
      [ _skater( 7, 16.0 ) ],
      slots,
      DepthGroup.defense() )
   eighth = SlotFiller.implied( slots, 8 )
   assert abs( lineup.implied - ( 80.0 + 16.0 + eighth ) ) < 0.001
