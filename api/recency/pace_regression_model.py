from __future__ import annotations

from dataclasses import dataclass, field

from .production_coefficient import ProductionCoefficient
from .production_growth import ProductionGrowth
from .production_weight import ProductionWeight
from ..projections.scoring_component_shares import ScoringComponentShares
from ..types import Types


@dataclass( frozen=True )
class PaceRegressionModel():
   scoring_growth: list[ ProductionGrowth ]
   component_shares: list[ ScoringComponentShares ] = field( default_factory=list )
   pim_coefficients: list[ ProductionCoefficient ] = field( default_factory=list )
   shots_coefficients: list[ ProductionCoefficient ] = field( default_factory=list )
   history_weights: list[ ProductionWeight ] = field( default_factory=list )


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> PaceRegressionModel:
      return cls(
         [ ProductionGrowth.from_row( item ) for item in row[ 'scoring' ][ 'growth' ] ],
         [ ScoringComponentShares.from_row( item ) for item in row[ 'component_shares' ] ],
         [ ProductionCoefficient.from_row( item ) for item in row[ 'pim' ][ 'coefficients' ] ],
         [ ProductionCoefficient.from_row( item ) for item in row[ 'shots' ][ 'coefficients' ] ],
         [ ProductionWeight.from_row( item ) for item in row[ 'scoring' ][ 'history_weights' ] ] )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'scoring': {
            'growth': [ growth.to_dict() for growth in self.scoring_growth ],
            'history_weights': [ weight.to_dict() for weight in self.history_weights ],
         },
         'component_shares': [ shares.to_dict() for shares in self.component_shares ],
         'pim': { 'coefficients': [ coefficient.to_dict() for coefficient in self.pim_coefficients ] },
         'shots': { 'coefficients': [ coefficient.to_dict() for coefficient in self.shots_coefficients ] },
      }
