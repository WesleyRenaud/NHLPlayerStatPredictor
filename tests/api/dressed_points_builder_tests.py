from __future__ import annotations

from api.depth_group import DepthGroup
from api.dressed_points_builder import DressedPointsBuilder
from api.games_share import GamesShare
from api.slot_average import SlotAverage
from api.slot_filler import SlotFiller
from api.teammate_skater import TeammateSkater


def Test_Build_TestFullSix_ExpectNoFill() -> None:
   present = [
      TeammateSkater( index, 20.0, GamesShare.FULL, None )
      for index in range( 1, 7 )
   ]
   points = DressedPointsBuilder.build(
      present,
      [ TeammateSkater( 7, 10.0, GamesShare.FULL, None ) ],
      [],
      DepthGroup.defense() )
   assert abs( points.total - 120.0 ) < 0.001


def Test_Build_TestOneMissing_ExpectExtraPoints() -> None:
   present = [
      TeammateSkater( index, 20.0, GamesShare.FULL, None )
      for index in range( 1, 6 )
   ]
   points = DressedPointsBuilder.build(
      present,
      [ TeammateSkater( 7, 10.0, GamesShare.FULL, None ) ],
      [],
      DepthGroup.defense() )
   assert abs( points.total - 110.0 ) < 0.001


def Test_Build_TestTwoMissing_ExpectExtraThenSlotEight() -> None:
   present = [
      TeammateSkater( index, 20.0, GamesShare.FULL, None )
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
         80.0 + extra.contribution + SlotFiller.contribution( slots, 8 ) )
      ) < 0.001
