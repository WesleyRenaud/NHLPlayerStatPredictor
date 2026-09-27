from __future__ import annotations

from .pace_regression import PaceRegression
from .pace_regression_model import PaceRegressionModel
from .playoff_pace_adjuster import PlayoffPaceAdjuster
from .prior_source import PriorSource
from .prior_year import PriorYear
from ..projections.season_pace import SeasonPace
from ..shared.enums.position import Position


class PaceRegressionPredictor():
   @classmethod
   def pace(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         year: int ) -> SeasonPace | None:
      regressed = cls.regressed( model.regressions, priors )

      if regressed is None:
         return None

      latest = priors[ Position.FIRST ]

      if latest.source() != PriorSource.NHL:
         return regressed

      adjusted = PlayoffPaceAdjuster.adjust(
         regressed,
         latest.playoff_surplus,
         model.playoff_goal_weight,
         model.playoff_assist_weight )

      if not latest.gap_before( year ):
         return adjusted

      return SeasonPace(
         goals=adjusted.goals * model.nhl_gap_goals,
         assists=adjusted.assists * model.nhl_gap_assists )


   @classmethod
   def regressed(
         cls,
         regressions: list[ PaceRegression ],
         priors: list[ PriorYear ] ) -> SeasonPace | None:
      if not priors:
         return None

      latest = priors[ Position.FIRST ]

      for width in range( len( priors ), 0, -1 ):
         for regression in regressions:
            if regression.covers( latest.source(), latest.target_age(), width ):
               return regression.pace( priors[ :width ] )

      return None
