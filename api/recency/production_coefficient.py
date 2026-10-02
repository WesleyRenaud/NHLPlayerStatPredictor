from __future__ import annotations

from dataclasses import dataclass

from ..types import Types


@dataclass( frozen=True )
class ProductionCoefficient():
   from_age: int
   to_age: int
   multiplier: float
   weight: float
   samples: int


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ProductionCoefficient:
      return cls(
         from_age=int( row[ 'from_age' ] ),
         to_age=int( row[ 'to_age' ] ),
         multiplier=float( row[ 'multiplier' ] ),
         weight=float( row[ 'weight' ] ),
         samples=int( row[ 'samples' ] ) )


   def to_dict( self ) -> dict[ str, int | float ]:
      return {
         'from_age': self.from_age,
         'to_age': self.to_age,
         'multiplier': self.multiplier,
         'weight': self.weight,
         'samples': self.samples,
      }
