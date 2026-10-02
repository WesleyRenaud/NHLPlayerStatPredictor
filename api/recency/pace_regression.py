from __future__ import annotations

from dataclasses import dataclass

from .prior_source import PriorSource
from .production_coefficient import ProductionCoefficient
from ..projections.scoring_stat import ScoringStat
from ..types import Types


@dataclass( frozen=True )
class PaceRegression():
   source: PriorSource
   stat: ScoringStat
   coefficients: list[ ProductionCoefficient ]


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> PaceRegression:
      return cls(
         source=PriorSource( str( row[ 'source' ] ) ),
         stat=ScoringStat( str( row[ 'stat' ] ) ),
         coefficients=[ ProductionCoefficient.from_row( item ) for item in row[ 'coefficients' ] ] )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'source': self.source.value,
         'stat': self.stat.value,
         'coefficients': [ coefficient.to_dict() for coefficient in self.coefficients ],
      }
