from __future__ import annotations

from dataclasses import dataclass

from .types import Types


@dataclass( frozen=True )
class RecencyWeight():
   lag: int
   weight: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> RecencyWeight:
      return cls(
         lag=int( row[ 'lag' ] ),
         weight=float( row[ 'weight' ] ) )


   def to_dict( self ) -> dict[ str, int | float ]:
      return {
         'lag': self.lag,
         'weight': self.weight,
      }
