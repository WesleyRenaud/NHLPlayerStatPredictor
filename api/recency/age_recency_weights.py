from __future__ import annotations

from dataclasses import dataclass

from .recency_weight import RecencyWeight
from ..shared.enums.position import Position
from ..types import Types


@dataclass( frozen=True )
class AgeRecencyWeights():
   age: int
   weights: list[ RecencyWeight ]


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> AgeRecencyWeights:
      return cls(
         age=int( row[ 'age' ] ),
         weights=[
         RecencyWeight.from_row( weight )
         for weight in list( row[ 'weights' ] )
      ] )


   def to_dict( self ) -> dict[ str, int | list[ dict[ str, int | float ] ] ]:
      return {
         'age': self.age,
         'weights': [ weight.to_dict() for weight in self.weights ],
      }


   @classmethod
   def for_age(
         cls,
         rows: list[ AgeRecencyWeights ],
         age: int ) -> list[ RecencyWeight ]:
      closest = rows[ Position.FIRST ]

      for row in rows:
         if abs( row.age - age ) < abs( closest.age - age ):
            closest = row

      return closest.weights
