from __future__ import annotations

from api.depth.league_filler import LeagueFiller


def Test_PlayerId_TestSlot_ExpectNegativeSlot() -> None:
   slot = 7

   player_id = LeagueFiller.player_id( slot )

   assert player_id == -slot


def Test_Slot_TestFillerId_ExpectSlotNumber() -> None:
   slot = 13

   resolved = LeagueFiller.slot( -slot )

   assert resolved == slot


def Test_IsFiller_TestFillerAndPlayer_ExpectOnlyFiller() -> None:
   slot = 7
   player_id = 1

   filler = LeagueFiller.is_filler( LeagueFiller.player_id( slot ) )
   skater = LeagueFiller.is_filler( player_id )

   assert filler
   assert not skater
