from __future__ import annotations

from api.depth.slot_average import SlotAverage


def Test_ToDict_TestSlot_ExpectRoundedFields() -> None:
   slot = SlotAverage( 7, 14.936, 2.581, 12.382 )

   payload = slot.to_dict()
   rebuilt = SlotAverage.from_row( payload )

   assert payload[ 'toi' ] == round( slot.toi, 2 )
   assert payload[ 'points' ] == round( slot.contribution, 2 )
   assert rebuilt.slot == payload[ 'slot' ]
   assert abs( rebuilt.contribution - rebuilt.goals - rebuilt.assists ) < 0.001
