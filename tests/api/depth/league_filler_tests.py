from __future__ import annotations

from api.depth.league_filler import LeagueFiller


def Test_PlayerId_TestSlot_ExpectNegativeSlot() -> None:
   assert LeagueFiller.player_id( 7 ) == -7


def Test_Slot_TestFillerId_ExpectSlotNumber() -> None:
   assert LeagueFiller.slot( -13 ) == 13


def Test_IsFiller_TestFillerAndPlayer_ExpectOnlyFiller() -> None:
   assert LeagueFiller.is_filler( LeagueFiller.player_id( 7 ) )
   assert not LeagueFiller.is_filler( 1 )
