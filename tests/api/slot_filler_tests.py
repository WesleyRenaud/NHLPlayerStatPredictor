from __future__ import annotations

from api.depth_group import DepthGroup
from api.last_core import LastCore
from api.shared.enums.position import Position
from api.slot_average import SlotAverage
from api.slot_filler import SlotFiller
from api.team import Team


def Test_Implied_TestKnownSlot_ExpectLastToi() -> None:
   slots = [ SlotAverage( 7, 15.0, 2.0, 12.0 ) ]
   assert SlotFiller.implied( slots, 7 ) == 15.0


def Test_Contribution_TestKnownSlot_ExpectContribution() -> None:
   slots = [ SlotAverage( 7, 15.0, 2.0, 12.0 ) ]
   assert SlotFiller.contribution( slots, 7 ) == 14.0


def Test_PadExtras_TestEmpty_ExpectLeagueSeventh() -> None:
   slots = [ SlotAverage( 7, 15.0, 2.0, 12.0 ) ]
   extras = SlotFiller.pad_extras(
      [],
      slots,
      DepthGroup.defense(),
      list( Team )[ Position.FIRST ] )
   assert len( extras ) == LastCore.EXTRA
   assert extras[ Position.FIRST ].implied == SlotFiller.implied( slots, 7 )
   assert extras[ Position.FIRST ].last_toi == 15.0
