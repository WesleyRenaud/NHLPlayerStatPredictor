from __future__ import annotations

from api.depth.depth_group import DepthGroup
from api.depth.dressed_filler import DressedFiller


def Test_Fill_TestPresentExtrasFills_ExpectCap() -> None:
   present = [ 20.0, 19.0 ]
   extras = [ 16.0 ]
   fills = [ 13.0, 12.0 ]
   count = 4

   dressed = DressedFiller.fill( present, extras, fills, count )

   assert dressed == [ *present, *extras, *fills ][ : count ]


def Test_SpareSlot_TestUsedExtra_ExpectNextAfterExtras() -> None:
   group = DepthGroup.defense()
   short = 5
   extras = 1

   after_one = DressedFiller.spare_slot( short, extras, group )
   unused = DressedFiller.spare_slot( group.dressed_count, extras, group )

   assert after_one == group.spare_slot + extras
   assert unused == group.spare_slot
