from __future__ import annotations

from dataclasses import dataclass

from .production_trajectory_share import ProductionTrajectoryShare
from ..types import Types


@dataclass( frozen=True )
class ProductionTrajectoryFit():
   move: float
   by_age: list[ ProductionTrajectoryShare ]


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ProductionTrajectoryFit:
      return cls(
         float( row[ 'move' ] ),
         [ ProductionTrajectoryShare.from_row( item ) for item in row[ 'by_age' ] ] )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'move': self.move,
         'by_age': [ share.to_dict() for share in self.by_age ],
      }


   @classmethod
   def empty( cls ) -> ProductionTrajectoryFit:
      return cls( 0.0, [] )
