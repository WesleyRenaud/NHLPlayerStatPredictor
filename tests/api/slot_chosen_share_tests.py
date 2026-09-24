from __future__ import annotations

from api.skater_group import SkaterGroup
from api.slot_chosen_share import SlotChosenShare


def Test_ToDict_TestShare_ExpectRoundedFields() -> None:
   payload = SlotChosenShare( 12, SkaterGroup( 'F' ), 0.5046, 0.5607 ).to_dict()
   rebuilt = SlotChosenShare.from_row( payload )
   assert payload[ 'dress_share' ] == 0.505
   assert payload[ 'chosen' ] == 0.561
   assert rebuilt.slot == payload[ 'slot' ]
   assert rebuilt.skater_group is SkaterGroup( payload[ 'skater_group' ] )
