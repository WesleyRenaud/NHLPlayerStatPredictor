from __future__ import annotations

from .pace_regression import PaceRegression
from .pace_regression_model import PaceRegressionModel
from .pim_regression_model import PimRegressionModel
from .pim_regression_predictor import PimRegressionPredictor
from .playoff_pace_adjuster import PlayoffPaceAdjuster
from .prior_source import PriorSource
from .prior_year import PriorYear
from ..projections.pace_values import PaceValues
from ..projections.scoring_paces import ScoringPaces
from ..season import Season
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason


class PaceRegressionPredictor():
   @classmethod
   def paces(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         target_season_id: int,
         pim_model: PimRegressionModel,
         nhl_seasons: list[ NhlSkaterSeason ] ) -> PaceValues | None:
      regressed = cls.regressed_paces( model.regressions, priors )

      if regressed is None:
         return None

      year = Season.start_year( target_season_id )
      pim_pace = PimRegressionPredictor.pace(
         pim_model,
         nhl_seasons,
         target_season_id )
      latest = priors[ Position.FIRST ]

      if latest.source() != PriorSource.NHL:
         return PaceValues(
            goals=regressed.goals,
            assists=regressed.assists,
            power_play_goals=regressed.power_play_goals,
            power_play_assists=regressed.power_play_assists,
            short_handed_goals=regressed.short_handed_goals,
            short_handed_assists=regressed.short_handed_assists,
            penalty_minutes=pim_pace )

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
            short_handed_assists=regressed.short_handed_assists,
            penalty_minutes=pim_pace )

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
            regressed.short_handed_assists * model.nhl_gap_short_handed_assists ),
         penalty_minutes=pim_pace )


   @classmethod
   def regressed_paces(
         cls,
         regressions: list[ PaceRegression ],
         priors: list[ PriorYear ] ) -> ScoringPaces | None:
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
