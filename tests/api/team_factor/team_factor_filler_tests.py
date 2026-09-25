from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_group import DepthGroup
from api.depth.league_filler import LeagueFiller
from api.depth.slot_average import SlotAverage
from api.shared.enums.position import Position
from api.team_factor.team_factor_filler import TeamFactorFiller
from api.team_factor.teammate_skater import TeammateSkater


def Test_Pad_TestFourSpares_ExpectAllFour() -> None:
   group = DepthGroup.defense()
   slots = [
      SlotAverage( group.spare_slot + Position.FIRST, 15.0, 2.0, 12.0 ),
      SlotAverage( group.spare_slot + Position.SECOND, 14.0, 1.5, 10.0 ),
      SlotAverage( group.spare_slot + Position.THIRD, 13.0, 1.0, 8.0 ),
      SlotAverage( group.spare_slot + Position.FOURTH, 12.0, 0.5, 6.0 ),
   ]
   extras = TeamFactorFiller.pad( [], slots, group.spare_slot )
   assert [ skater.player_id for skater in extras ] == [
      LeagueFiller.player_id( slot.slot )
      for slot in slots
   ]
   assert extras[ Position.LAST ].contribution == slots[ Position.LAST ].contribution


def Test_ExtraPace_TestNamed_ExpectRosterPace() -> None:
   player_id = 7
   pace = 18.0

   extra_pace = TeamFactorFiller.extra_pace( player_id, { player_id: pace }, [] )

   assert extra_pace == pace


def Test_ExtraPace_TestMissingNamed_ExpectZero() -> None:
   extra_pace = TeamFactorFiller.extra_pace( 7, {}, [] )

   assert extra_pace == 0.0


def Test_ExtraPace_TestFiller_ExpectSlotContribution() -> None:
   slots = [ SlotAverage( 7, 15.0, 2.0, 12.0 ) ]

   extra_pace = TeamFactorFiller.extra_pace(
      LeagueFiller.player_id( 7 ),
      {},
      slots )

   assert extra_pace == slots[ Position.FIRST ].contribution


def Test_Pad_TestExistingExtra_ExpectLaterSlots() -> None:
   group = DepthGroup.defense()
   slots = [
      SlotAverage( group.spare_slot + Position.FIRST, 15.0, 2.0, 12.0 ),
      SlotAverage( group.spare_slot + Position.SECOND, 14.0, 1.5, 10.0 ),
      SlotAverage( group.spare_slot + Position.THIRD, 13.0, 1.0, 8.0 ),
   ]
   extras = TeamFactorFiller.pad(
      [ TeammateSkater( 7, 18.0, GamesShare.FULL, None ) ],
      slots,
      group.spare_slot )
   assert extras[ Position.FIRST ].player_id == 7
   assert [ skater.player_id for skater in extras[ Position.SECOND: ] ] == [
      LeagueFiller.player_id( slots[ Position.SECOND ].slot ),
      LeagueFiller.player_id( slots[ Position.LAST ].slot ),
   ]
