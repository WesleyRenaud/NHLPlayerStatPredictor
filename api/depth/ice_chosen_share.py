from __future__ import annotations

from dataclasses import dataclass

from ..skaters.skater_group import SkaterGroup
from ..types import Types


@dataclass( frozen=True )
class IceChosenShare():
   toi: float
   skater_group: SkaterGroup
   dress_share: float
   chosen: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> IceChosenShare:
      return cls(
         float( row[ 'toi' ] ),
         SkaterGroup( str( row[ 'skater_group' ] ) ),
         float( row[ 'dress_share' ] ),
         float( row[ 'chosen' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'toi': round( self.toi, 1 ),
         'skater_group': self.skater_group.value,
         'dress_share': round( self.dress_share, 3 ),
         'chosen': round( self.chosen, 3 ),
      }
