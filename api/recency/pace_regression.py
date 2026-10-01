from __future__ import annotations

from dataclasses import dataclass

from .age_band import AgeBand
from .prior_source import PriorSource
from .prior_year import PriorYear
from ..projections.pace_values import PaceValues
from ..types import Types


@dataclass( frozen=True )
class PaceRegression():
   source: PriorSource
   band: AgeBand
   goal_constant: float
   goal_weights: list[ float ]
   assist_constant: float
   assist_weights: list[ float ]
   power_play_goal_constant: float
   power_play_goal_weights: list[ float ]
   power_play_assist_constant: float
   power_play_assist_weights: list[ float ]
   short_handed_goal_constant: float
   short_handed_goal_weights: list[ float ]
   short_handed_assist_constant: float
   short_handed_assist_weights: list[ float ]


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> PaceRegression:
      return cls(
         source=PriorSource( str( row[ 'source' ] ) ),
         band=AgeBand( int( row[ 'first_age' ] ), int( row[ 'last_age' ] ) ),
         goal_constant=float( row[ 'goal_constant' ] ),
         goal_weights=[ float( weight ) for weight in row[ 'goal_weights' ] ],
         assist_constant=float( row[ 'assist_constant' ] ),
         assist_weights=[ float( weight ) for weight in row[ 'assist_weights' ] ],
         power_play_goal_constant=float( row[ 'power_play_goal_constant' ] ),
         power_play_goal_weights=[ float( weight ) for weight in row[ 'power_play_goal_weights' ] ],
         power_play_assist_constant=float( row[ 'power_play_assist_constant' ] ),
         power_play_assist_weights=[ float( weight ) for weight in row[ 'power_play_assist_weights' ] ],
         short_handed_goal_constant=float( row[ 'short_handed_goal_constant' ] ),
         short_handed_goal_weights=[ float( weight ) for weight in row[ 'short_handed_goal_weights' ] ],
         short_handed_assist_constant=float( row[ 'short_handed_assist_constant' ] ),
         short_handed_assist_weights=[ float( weight ) for weight in row[ 'short_handed_assist_weights' ] ] )


   def covers( self, source: PriorSource, age: int, width: int ) -> bool:
      return (
         self.source == source
         and self.band.contains( age )
         and len( self.goal_weights ) == width )


   def paces( self, priors: list[ PriorYear ] ) -> PaceValues:
      goals = self.goal_constant + sum(
         weight * prior.pace.goals
         for weight, prior in zip( self.goal_weights, priors ) )
      assists = self.assist_constant + sum(
         weight * prior.pace.assists
         for weight, prior in zip( self.assist_weights, priors ) )
      power_play_goals = self.power_play_goal_constant + sum(
         weight * prior.power_play_pace.goals
         for weight, prior in zip( self.power_play_goal_weights, priors ) )
      power_play_assists = self.power_play_assist_constant + sum(
         weight * prior.power_play_pace.assists
         for weight, prior in zip( self.power_play_assist_weights, priors ) )
      short_handed_goals = self.short_handed_goal_constant + sum(
         weight * prior.short_handed_pace.goals
         for weight, prior in zip( self.short_handed_goal_weights, priors ) )
      short_handed_assists = self.short_handed_assist_constant + sum(
         weight * prior.short_handed_pace.assists
         for weight, prior in zip( self.short_handed_assist_weights, priors ) )
      return PaceValues(
         goals=goals,
         assists=assists,
         power_play_goals=power_play_goals,
         power_play_assists=power_play_assists,
         short_handed_goals=short_handed_goals,
         short_handed_assists=short_handed_assists )


   def to_dict( self ) -> dict[ str, str | int | float | list[ float ] ]:
      return {
         'source': self.source.value,
         'first_age': self.band.first_age,
         'last_age': self.band.last_age,
         'goal_constant': self.goal_constant,
         'goal_weights': self.goal_weights,
         'assist_constant': self.assist_constant,
         'assist_weights': self.assist_weights,
         'power_play_goal_constant': self.power_play_goal_constant,
         'power_play_goal_weights': self.power_play_goal_weights,
         'power_play_assist_constant': self.power_play_assist_constant,
         'power_play_assist_weights': self.power_play_assist_weights,
         'short_handed_goal_constant': self.short_handed_goal_constant,
         'short_handed_goal_weights': self.short_handed_goal_weights,
         'short_handed_assist_constant': self.short_handed_assist_constant,
         'short_handed_assist_weights': self.short_handed_assist_weights,
      }
