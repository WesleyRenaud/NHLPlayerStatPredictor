from __future__ import annotations

from dataclasses import dataclass

from .production_coefficient import ProductionCoefficient
from ..types import Types


@dataclass( frozen=True )
class PimRegressionModel():
   coefficients: list[ ProductionCoefficient ]


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> PimRegressionModel:
      return cls( [ ProductionCoefficient.from_row( item ) for item in row[ 'coefficients' ] ] )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'coefficients': [ coefficient.to_dict() for coefficient in self.coefficients ],
      }
