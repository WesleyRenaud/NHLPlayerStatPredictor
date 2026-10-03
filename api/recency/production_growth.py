from __future__ import annotations

from dataclasses import dataclass

from ..types import Types


@dataclass( frozen=True )
class ProductionGrowth():
   from_age: int
   to_age: int
   multiplier: float
   samples: int


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ProductionGrowth:
      return cls( int( row[ 'from_age' ] ), int( row[ 'to_age' ] ),
         float( row[ 'multiplier' ] ), int( row[ 'samples' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'from_age': self.from_age,
         'to_age': self.to_age,
         'multiplier': self.multiplier,
         'samples': self.samples,
      }
