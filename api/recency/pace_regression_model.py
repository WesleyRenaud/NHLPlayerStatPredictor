from __future__ import annotations

from dataclasses import dataclass, field

from .pace_regression import PaceRegression
from ..projections.scoring_component_shares import ScoringComponentShares
from ..types import Types


@dataclass( frozen=True )
class PaceRegressionModel():
   regressions: list[ PaceRegression ]
   component_shares: list[ ScoringComponentShares ] = field( default_factory=list )


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> PaceRegressionModel:
      return cls(
         [ PaceRegression.from_row( item ) for item in row[ 'regressions' ] ],
         [ ScoringComponentShares.from_row( item ) for item in row[ 'component_shares' ] ] )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'regressions': [ regression.to_dict() for regression in self.regressions ],
         'component_shares': [ shares.to_dict() for shares in self.component_shares ],
      }
