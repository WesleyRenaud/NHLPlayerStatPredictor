from __future__ import annotations

from dataclasses import dataclass

from .pace_regression import PaceRegression
from ..types import Types


@dataclass( frozen=True )
class PaceRegressionModel():
   regressions: list[ PaceRegression ]
   nhl_gap_goals: float
   nhl_gap_assists: float
   playoff_goal_weight: float
   playoff_assist_weight: float
   nhl_gap_power_play_goals: float
   nhl_gap_power_play_assists: float
   nhl_gap_short_handed_goals: float
   nhl_gap_short_handed_assists: float


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> PaceRegressionModel:
      return cls(
         regressions=[ PaceRegression.from_row( item ) for item in row[ 'regressions' ] ],
         nhl_gap_goals=float( row[ 'nhl_gap_goals' ] ),
         nhl_gap_assists=float( row[ 'nhl_gap_assists' ] ),
         playoff_goal_weight=float( row[ 'playoff_goal_weight' ] ),
         playoff_assist_weight=float( row[ 'playoff_assist_weight' ] ),
         nhl_gap_power_play_goals=float( row[ 'nhl_gap_power_play_goals' ] ),
         nhl_gap_power_play_assists=float( row[ 'nhl_gap_power_play_assists' ] ),
         nhl_gap_short_handed_goals=float( row[ 'nhl_gap_short_handed_goals' ] ),
         nhl_gap_short_handed_assists=float( row[ 'nhl_gap_short_handed_assists' ] ) )


   def to_dict( self ) -> dict[ str, float | list[ dict[ str, str | int | float | list[ float ] ] ] ]:
      return {
         'regressions': [ regression.to_dict() for regression in self.regressions ],
         'nhl_gap_goals': self.nhl_gap_goals,
         'nhl_gap_assists': self.nhl_gap_assists,
         'playoff_goal_weight': self.playoff_goal_weight,
         'playoff_assist_weight': self.playoff_assist_weight,
         'nhl_gap_power_play_goals': self.nhl_gap_power_play_goals,
         'nhl_gap_power_play_assists': self.nhl_gap_power_play_assists,
         'nhl_gap_short_handed_goals': self.nhl_gap_short_handed_goals,
         'nhl_gap_short_handed_assists': self.nhl_gap_short_handed_assists,
      }
