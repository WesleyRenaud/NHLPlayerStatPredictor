from __future__ import annotations

from dataclasses import dataclass

from ..types import Types


@dataclass( frozen=True )
class ProductionKeepFit():
   kept_above: float = 0.0


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ProductionKeepFit:
      return cls( float( row[ 'kept_above' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return { 'kept_above': self.kept_above }


   @classmethod
   def empty( cls ) -> ProductionKeepFit:
      return cls()
