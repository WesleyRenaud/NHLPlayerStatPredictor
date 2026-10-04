from __future__ import annotations

import pytest

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


@pytest.mark.parametrize( 'group', [ DepthGroup.defense(), DepthGroup.forwards() ] )
def Test_Build_TestZeroRegular_ExpectReplacementSlot( group: DepthGroup ) -> None:
   implied = 20.0
   replacement = SlotAverage( group.spare_slot, 12.0, 0.0, 0.0 )
   present = [
      *[ _skater( index, implied ) for index in range( 1, group.dressed_count ) ],
      _skater( group.dressed_count, 0.0 ),
   ]

   lineup = DressedLineupBuilder.build( present, [], [ replacement ], group )

   assert lineup.ice == [ *[ implied ] * ( group.dressed_count - 1 ), replacement.toi ]


def Test_Build_TestZeroExtraBeforeUsableExtra_ExpectUsableThenReplacement() -> None:
   group = DepthGroup.defense()
   implied = 20.0
   extra_implied = 16.0
   first_spare = SlotAverage( group.spare_slot, 14.0, 0.0, 0.0 )
   next_spare = SlotAverage( group.spare_slot + 1, 12.0, 0.0, 0.0 )
   present = [ _skater( index, implied ) for index in range( 1, group.dressed_count - 1 ) ]
   extras = [ _skater( 7, 0.0 ), _skater( 8, extra_implied ) ]

   lineup = DressedLineupBuilder.build( present, extras, [ first_spare, next_spare ], group )

   assert lineup.ice == [ *[ implied ] * len( present ), extra_implied, next_spare.toi ]


def Test_Build_TestZeroRegularAndExtra_ExpectConsecutiveReplacementSlots() -> None:
   group = DepthGroup.defense()
   implied = 20.0
   replacements = [
      SlotAverage( group.spare_slot, 14.0, 0.0, 0.0 ),
      SlotAverage( group.spare_slot + 1, 12.0, 0.0, 0.0 ),
   ]
   present = [
      *[ _skater( index, implied ) for index in range( 1, group.dressed_count - 1 ) ],
      _skater( group.dressed_count - 1, 0.0 ),
   ]

   lineup = DressedLineupBuilder.build( present, [ _skater( 7, 0.0 ) ], replacements, group )

   assert lineup.ice == [
      *[ implied ] * ( group.dressed_count - 2 ),
      *[ average.toi for average in replacements ],
   ]
