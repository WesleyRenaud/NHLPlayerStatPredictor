from __future__ import annotations

from api.depth.depth_group import DepthGroup
from api.depth.last_core import LastCore
from api.depth.slot_average import SlotAverage
from api.depth.slot_filler import SlotFiller
from api.shared.enums.position import Position
from api.skaters.team import Team


def Test_Implied_TestKnownSlot_ExpectLastToi() -> None:
   slot = SlotAverage( 7, 15.0, 2.0, 12.0 )

   implied = SlotFiller.implied( [ slot ], slot.slot )

   assert implied == slot.toi


def Test_Contribution_TestKnownSlot_ExpectContribution() -> None:
   slot = SlotAverage( 7, 15.0, 2.0, 12.0 )

   contribution = SlotFiller.contribution( [ slot ], slot.slot )

   assert contribution == slot.contribution


def Test_PadExtras_TestEmpty_ExpectLeagueSeventh() -> None:
   slot = SlotAverage( 7, 15.0, 2.0, 12.0 )
   slots = [ slot ]

   extras = SlotFiller.pad_extras(
      [],
      slots,
      DepthGroup.defense(),
      list( Team )[ Position.FIRST ] )

   assert len( extras ) == LastCore.EXTRA
   assert extras[ Position.FIRST ].implied == slot.toi
   assert extras[ Position.FIRST ].last_toi == slot.toi
