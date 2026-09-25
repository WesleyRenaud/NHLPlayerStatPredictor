from __future__ import annotations

from api.depth.slot_average import SlotAverage


def Test_ToDict_TestSlot_ExpectRoundedFields() -> None:
   payload = SlotAverage( 7, 14.936, 2.581, 12.382 ).to_dict()
   rebuilt = SlotAverage.from_row( payload )
   assert payload[ 'toi' ] == 14.94
   assert payload[ 'points' ] == 14.96
   assert rebuilt.slot == payload[ 'slot' ]
   assert abs( rebuilt.contribution - rebuilt.goals - rebuilt.assists ) < 0.001
