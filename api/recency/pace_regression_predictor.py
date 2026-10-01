from __future__ import annotations

from .pace_regression import PaceRegression
from .pace_regression_model import PaceRegressionModel
from .playoff_pace_adjuster import PlayoffPaceAdjuster
from .prior_source import PriorSource
from .prior_year import PriorYear
from ..projections.pace_values import PaceValues
from ..projections.season_pace import SeasonPace
from ..shared.enums.position import Position


class PaceRegressionPredictor():
   @classmethod
   def paces(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         year: int ) -> PaceValues | None:
      regressed = cls.regressed_paces( model.regressions, priors )

      if regressed is None:
         return None

      latest = priors[ Position.FIRST ]

      if latest.source() != PriorSource.NHL:
         return regressed

      adjusted = PlayoffPaceAdjuster.adjust(
         regressed.season_pace(),
         latest.playoff_surplus,
         model.playoff_goal_weight,
         model.playoff_assist_weight )

      if not latest.gap_before( year ):
         return PaceValues(
            goals=adjusted.goals,
            assists=adjusted.assists,
            power_play_goals=regressed.power_play_goals,
            power_play_assists=regressed.power_play_assists,
            short_handed_goals=regressed.short_handed_goals,
            short_handed_assists=regressed.short_handed_assists )

      return PaceValues(
         goals=adjusted.goals * model.nhl_gap_goals,
         assists=adjusted.assists * model.nhl_gap_assists,
         power_play_goals=(
            regressed.power_play_goals * model.nhl_gap_power_play_goals ),
         power_play_assists=(
            regressed.power_play_assists * model.nhl_gap_power_play_assists ),
         short_handed_goals=(
            regressed.short_handed_goals * model.nhl_gap_short_handed_goals ),
         short_handed_assists=(
            regressed.short_handed_assists * model.nhl_gap_short_handed_assists ) )


   @classmethod
   def regressed_paces(
         cls,
         regressions: list[ PaceRegression ],
         priors: list[ PriorYear ] ) -> PaceValues | None:
      regression = cls._regression( regressions, priors )
      return (
         None if regression is None
         else regression.paces( priors[ :len( regression.goal_weights ) ] ) )


   @classmethod
   def _regression(
         cls,
         regressions: list[ PaceRegression ],
         priors: list[ PriorYear ] ) -> PaceRegression | None:
      if not priors:
         return None

      latest = priors[ Position.FIRST ]

      for width in range( len( priors ), 0, -1 ):
         for regression in regressions:
            if regression.covers( latest.source(), latest.target_age(), width ):
               return regression

      return None
