from __future__ import annotations

from .pace_regression import PaceRegression
from .pace_regression_model import PaceRegressionModel
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

      if regressed is None or not cls._is_returning_nhl_player( priors, year ):
         return regressed

      return SeasonPace(
         goals=regressed.goals * model.nhl_gap_goals,
         assists=regressed.assists * model.nhl_gap_assists )


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


   @classmethod
   def _is_returning_nhl_player( cls, priors: list[ PriorYear ], year: int ) -> bool:
      latest = priors[ Position.FIRST ]
      return latest.source() == PriorSource.NHL and latest.gap_before( year ) > 0
