from __future__ import annotations

from functools import partial

from ..depth.nhl_player_season_ice_scale import NhlPlayerSeasonIceScale
from .nhl_production_regression import NhlProductionRegression
from .nhl_production_stat import NhlProductionStat
from .pace_regression_model import PaceRegressionModel
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from .production_history_predictor import ProductionHistoryPredictor
from .production_season import ProductionSeason
from ..projections.pace_values import PaceValues
from ..projections.scoring_stat import ScoringStat
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
         nhl_seasons: list[ NhlSkaterSeason ],
         player_ice_scales: list[ NhlPlayerSeasonIceScale ] | None = None ) -> PaceValues | None:
      if not priors:
         return None

      year = Season.start_year( target_season_id )
      latest = priors[ Position.FIRST ]
      target_age = latest.age_in_year( year )
      projected_paces_by_stat: dict[ ScoringStat, float ] = {}
      nhl_priors = PriorYearBuilder.build( nhl_seasons, [], year, [], player_ice_scales )

      for stat in ScoringStat:
         projected_paces_by_stat[ stat ] = cls._pace( model, priors, target_age, stat )

      return PaceValues(
         **{ stat.value: pace for stat, pace in projected_paces_by_stat.items() },
         penalty_minutes=NhlProductionRegression.pace(
            model.pim_coefficients, nhl_priors, year, NhlProductionStat.PIM, model.trajectory ),
         shots=NhlProductionRegression.pace(
            model.shots_coefficients, nhl_priors, year, NhlProductionStat.SHOTS, model.trajectory ) )


   @classmethod
   def _pace(
         cls,
         model: PaceRegressionModel,
         priors: list[ PriorYear ],
         target_age: int,
         stat: ScoringStat ) -> float:
      if not priors:
         return 0.0

      return ProductionHistoryPredictor.pace(
         [ ProductionSeason( int( prior.age ), getattr( prior.scoring, stat.value ), prior.games ) for prior in priors ],
         target_age,
         partial( ProductionHistoryPredictor.coefficient, model.scoring_growth ),
         partial( ProductionHistoryPredictor.weight, model.history_weights ),
         model.trajectory )
