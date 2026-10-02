from __future__ import annotations

from dataclasses import dataclass

from .pace_regression import PaceRegression
from ..types import Types


@dataclass( frozen=True )
class PaceRegressionModel():
   regressions: list[ PaceRegression ]


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> PaceRegressionModel:
      return cls( [ PaceRegression.from_row( item ) for item in row[ 'regressions' ] ] )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'regressions': [ regression.to_dict() for regression in self.regressions ],
      }
