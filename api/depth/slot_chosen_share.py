from __future__ import annotations

from dataclasses import dataclass

from ..skaters.skater_group import SkaterGroup
from ..types import Types


@dataclass( frozen=True )
class SlotChosenShare():
   slot: int
   skater_group: SkaterGroup
   dress_share: float
   chosen: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> SlotChosenShare:
      return cls(
         slot=int( row[ 'slot' ] ),
         skater_group=SkaterGroup( str( row[ 'skater_group' ] ) ),
         dress_share=float( row[ 'dress_share' ] ),
         chosen=float( row[ 'chosen' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'slot': self.slot,
         'skater_group': self.skater_group.value,
         'dress_share': round( self.dress_share, 3 ),
         'chosen': round( self.chosen, 3 ),
      }
