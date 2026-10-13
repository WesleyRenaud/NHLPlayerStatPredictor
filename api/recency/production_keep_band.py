from __future__ import annotations

from dataclasses import dataclass

from ..types import Types


@dataclass( frozen=True )
class ProductionKeepBand():
   relative_slope_below: float
   kept_share: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ProductionKeepBand:
      return cls( float( row[ 'relative_slope_below' ] ), float( row[ 'kept_share' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'relative_slope_below': self.relative_slope_below,
         'kept_share': self.kept_share,
      }
