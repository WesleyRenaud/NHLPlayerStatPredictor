from __future__ import annotations

from functools import partial

from ..depth.nhl_player_season_ice_scale import NhlPlayerSeasonIceScale
from .nhl_production_regression import NhlProductionRegression
from .nhl_production_stat import NhlProductionStat
from .pace_regression_model import PaceRegressionModel
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from .production_growth import ProductionGrowth
from .production_history_predictor import ProductionHistoryPredictor
from .production_season import ProductionSeason
from .production_trajectory_fit import ProductionTrajectoryFit
from .production_trend import ProductionTrend
from .production_trend_line import ProductionTrendLine
from ..projections.pace_values import PaceValues
from ..projections.scoring_stat import ScoringStat
from ..season import Season
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason


class PaceRegressionPredictor():
   INCLUDED_GAMES = 10


   @classmethod
   def paces(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         target_season_id: int,
         nhl_seasons: list[ NhlSkaterSeason ],
         player_ice_scales: list[ NhlPlayerSeasonIceScale ] | None = None ) -> PaceValues | None:
      if not priors:
         return None

      priors = cls._history( priors )

      if not priors:
         return None

      year = Season.start_year( target_season_id )
      latest = priors[ Position.FIRST ]
      target_age = latest.age_in_year( year )
      projected_paces_by_stat: dict[ ScoringStat, float ] = {}
      nhl_priors = PriorYearBuilder.build( nhl_seasons, [], year, [], player_ice_scales )
      trend_seasons = ProductionTrend.seasons( nhl_seasons, year )

      for stat in ScoringStat:
         projected_paces_by_stat[ stat ] = cls._pace(
            model, priors, target_age, stat, model.trajectory, trend_seasons, year )

      return PaceValues(
         **{ stat.value: pace for stat, pace in projected_paces_by_stat.items() },
         penalty_minutes=NhlProductionRegression.pace(
            model.pim_coefficients, nhl_priors, year, NhlProductionStat.PIM, model.trajectory ),
         shots=NhlProductionRegression.pace(
            model.shots_coefficients, nhl_priors, year, NhlProductionStat.SHOTS, model.trajectory ) )


   @classmethod
   def _history( cls, priors: list[ PriorYear ] ) -> list[ PriorYear ]:
      arrived = priors[ Position.FIRST ].arrival is not None
      seen_nhl = False
      kept: list[ PriorYear ] = []

      for index, prior in enumerate( priors ):
         if prior.nhl_games:
            seen_nhl = True

            if prior.nhl_games >= cls.INCLUDED_GAMES:
               kept.append( prior )
         elif not seen_nhl and ( index == Position.FIRST or not arrived ):
            kept.append( prior )

      return kept


   @classmethod
   def _pace(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         target_age: int,
         stat: ScoringStat,
         trajectory: ProductionTrajectoryFit,
         trend_seasons: list[ NhlSkaterSeason ] | None,
         target_year: int ) -> float:
      if not priors:
         return 0.0

      if trend_seasons is not None:
         return cls._pace_from_trend( trend_seasons, stat, model.scoring_growth, target_year )

      return ProductionHistoryPredictor.pace(
         [
            ProductionSeason(
               prior.age,
               getattr( prior.scoring, stat.value ),
               prior.games,
               None if prior.arrival is None else getattr( prior.arrival, stat.value ) )
            for prior in priors
         ],
         target_age,
         partial( ProductionHistoryPredictor.coefficient, model.scoring_growth ),
         partial( ProductionHistoryPredictor.weight, model.history_weights ),
         trajectory )


   @classmethod
   def _pace_from_trend(
         cls,
         seasons: list[ NhlSkaterSeason ],
         stat: ScoringStat,
         growth: list[ ProductionGrowth ],
         target_year: int ) -> float:
      prior_seasons = seasons[ : Position.LAST ]
      latest = seasons[ Position.LAST ]
      point_line = ProductionTrendLine.fit( [ season.p_pace for season in prior_seasons ] )
      kept = ProductionTrend.kept( point_line.relative_slope )
      component_line = ProductionTrendLine.fit( [
         getattr( season.scoring_paces(), stat.value ) for season in prior_seasons
      ] )
      latest_pace = getattr( latest.scoring_paces(), stat.value )
      at_latest_age = ProductionTrend.at_latest( component_line.level, latest_pace, kept )
      target_age = latest.age_in_year( target_year )
      multiplier = ProductionHistoryPredictor.multiplier(
         partial( ProductionHistoryPredictor.coefficient, growth ),
         latest.age,
         target_age )

      return max( 0.0, at_latest_age * multiplier )
