from __future__ import annotations

from api.depth.ice_chosen_share import IceChosenShare
from api.skaters.skater_group import SkaterGroup


def Test_ToDict_TestShare_ExpectRoundedFields() -> None:
   share = IceChosenShare( 17.62, SkaterGroup( 'D' ), 0.5046, 0.5607 )

   payload = share.to_dict()
   rebuilt = IceChosenShare.from_row( payload )

   assert payload[ 'toi' ] == round( share.toi, 1 )
   assert payload[ 'dress_share' ] == round( share.dress_share, 3 )
   assert payload[ 'chosen' ] == round( share.chosen, 3 )
   assert rebuilt.toi == payload[ 'toi' ]
   assert rebuilt.skater_group is SkaterGroup( payload[ 'skater_group' ] )
