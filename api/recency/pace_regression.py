from __future__ import annotations

from dataclasses import dataclass

from .age_band import AgeBand
from .prior_source import PriorSource
from .prior_year import PriorYear
from ..projections.season_pace import SeasonPace
from ..types import Types


@dataclass( frozen=True )
class PaceRegression():
   source: PriorSource
   band: AgeBand
   goal_constant: float
   goal_weights: list[ float ]
   assist_constant: float
   assist_weights: list[ float ]


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> PaceRegression:
      return cls(
         source=PriorSource( str( row[ 'source' ] ) ),
         band=AgeBand( int( row[ 'first_age' ] ), int( row[ 'last_age' ] ) ),
         goal_constant=float( row[ 'goal_constant' ] ),
         goal_weights=[ float( weight ) for weight in row[ 'goal_weights' ] ],
         assist_constant=float( row[ 'assist_constant' ] ),
         assist_weights=[ float( weight ) for weight in row[ 'assist_weights' ] ] )


   def covers( self, source: PriorSource, age: int, width: int ) -> bool:
      return (
         self.source == source
         and self.band.contains( age )
         and len( self.goal_weights ) == width )


   def pace( self, priors: list[ PriorYear ] ) -> SeasonPace:
      goals = self.goal_constant + sum(
         weight * prior.pace.goals
         for weight, prior in zip( self.goal_weights, priors ) )
      assists = self.assist_constant + sum(
         weight * prior.pace.assists
         for weight, prior in zip( self.assist_weights, priors ) )
      return SeasonPace( goals=goals, assists=assists )


   def to_dict( self ) -> dict[ str, str | int | float | list[ float ] ]:
      return {
         'source': self.source.value,
         'first_age': self.band.first_age,
         'last_age': self.band.last_age,
         'goal_constant': self.goal_constant,
         'goal_weights': self.goal_weights,
         'assist_constant': self.assist_constant,
         'assist_weights': self.assist_weights,
      }
