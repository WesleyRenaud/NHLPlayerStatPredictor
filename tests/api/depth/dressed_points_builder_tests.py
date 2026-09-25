from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_group import DepthGroup
from api.depth.dressed_points_builder import DressedPointsBuilder
from api.depth.slot_average import SlotAverage
from api.depth.slot_filler import SlotFiller
from api.shared.enums.position import Position
from api.team_factor.teammate_skater import TeammateSkater


def Test_Build_TestFullSix_ExpectNoFill() -> None:
   pace = 20.0
   present = [
      TeammateSkater( index, pace, GamesShare.FULL, None )
      for index in range( 1, 7 )
   ]

   points = DressedPointsBuilder.build(
      present,
      [ TeammateSkater( 7, 10.0, GamesShare.FULL, None ) ],
      [],
      DepthGroup.defense() )

   assert abs( points.total - pace * len( present ) ) < 0.001


def Test_Build_TestOneMissing_ExpectExtraPoints() -> None:
   pace = 20.0
   extra = TeammateSkater( 7, 10.0, GamesShare.FULL, None )
   present = [
      TeammateSkater( index, pace, GamesShare.FULL, None )
      for index in range( 1, 6 )
   ]

   points = DressedPointsBuilder.build(
      present,
      [ extra ],
      [],
      DepthGroup.defense() )

   assert abs( points.total - ( pace * len( present ) + extra.contribution ) ) < 0.001


def Test_Build_TestTwoMissing_ExpectExtraThenSlotEight() -> None:
   pace = 20.0
   present = [
      TeammateSkater( index, pace, GamesShare.FULL, None )
      for index in range( 1, 5 )
   ]
   slots = [ SlotAverage( 8, 13.0, 1.0, 9.0 ) ]
   extra = TeammateSkater( 7, 10.0, GamesShare.FULL, None )

   points = DressedPointsBuilder.build(
      present,
      [ extra ],
      slots,
      DepthGroup.defense() )

   assert abs(
      points.total - (
         pace * len( present )
         + extra.contribution
         + SlotFiller.contribution( slots, slots[ Position.FIRST ].slot ) )
      ) < 0.001
