from __future__ import annotations

from api.depth.depth_group import DepthGroup
from api.depth.dressed_filler import DressedFiller


def Test_Fill_TestPresentExtrasFills_ExpectCap() -> None:
   assert DressedFiller.fill(
      [ 20.0, 19.0 ],
      [ 16.0 ],
      [ 13.0, 12.0 ],
      4 ) == [ 20.0, 19.0, 16.0, 13.0 ]


def Test_SpareSlot_TestUsedExtra_ExpectNextAfterExtras() -> None:
   group = DepthGroup.defense()
   assert DressedFiller.spare_slot( 5, 1, group ) == group.spare_slot + 1
   assert DressedFiller.spare_slot( 6, 1, group ) == group.spare_slot
