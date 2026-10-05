from __future__ import annotations

from dataclasses import dataclass

from ..types import Types


@dataclass( frozen=True )
class ProductionTrajectoryShare():
   age: int
   rise_share: float | None
   drop_share: float | None


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ProductionTrajectoryShare:
      rise_share = row[ 'rise_share' ]
      drop_share = row[ 'drop_share' ]
      return cls(
         int( row[ 'age' ] ),
         None if rise_share is None else float( rise_share ),
         None if drop_share is None else float( drop_share ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'age': self.age,
         'rise_share': self.rise_share,
         'drop_share': self.drop_share,
      }
