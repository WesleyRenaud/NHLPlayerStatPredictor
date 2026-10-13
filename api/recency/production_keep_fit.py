from __future__ import annotations

from dataclasses import dataclass, field

from .production_keep_band import ProductionKeepBand
from ..types import Types


@dataclass( frozen=True )
class ProductionKeepFit():
   bands: list[ ProductionKeepBand ] = field( default_factory=list )
   kept_above: float = 0.0


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ProductionKeepFit:
      return cls(
         [ ProductionKeepBand.from_row( item ) for item in row[ 'bands' ] ],
         float( row[ 'kept_above' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'bands': [ band.to_dict() for band in self.bands ],
         'kept_above': self.kept_above,
      }


   @classmethod
   def empty( cls ) -> ProductionKeepFit:
      return cls()


   def kept( self, relative_slope: float ) -> float:
      for band in self.bands:
         if relative_slope < band.relative_slope_below:
            return band.kept_share

      return self.kept_above
