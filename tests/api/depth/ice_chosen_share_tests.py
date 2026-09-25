from __future__ import annotations

from api.depth.ice_chosen_share import IceChosenShare
from api.skaters.skater_group import SkaterGroup


def Test_ToDict_TestShare_ExpectRoundedFields() -> None:
   payload = IceChosenShare( 17.62, SkaterGroup( 'D' ), 0.5046, 0.5607 ).to_dict()
   rebuilt = IceChosenShare.from_row( payload )
   assert payload[ 'toi' ] == 17.6
   assert payload[ 'dress_share' ] == 0.505
   assert payload[ 'chosen' ] == 0.561
   assert rebuilt.toi == payload[ 'toi' ]
   assert rebuilt.skater_group is SkaterGroup( payload[ 'skater_group' ] )
