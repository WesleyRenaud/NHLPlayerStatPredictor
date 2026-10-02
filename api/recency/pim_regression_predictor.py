from __future__ import annotations

from .pim_regression_model import PimRegressionModel
from .prior_year_builder import PriorYearBuilder
from .production_coefficient import ProductionCoefficient
from .production_history_predictor import ProductionHistoryPredictor
from ..season import Season
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason


class PimRegressionPredictor():
   @classmethod
   def pace(
         cls,
         model: PimRegressionModel,
         seasons: list[ NhlSkaterSeason ],
         target_season_id: int ) -> float | None:
      year = Season.start_year( target_season_id )
      priors = PriorYearBuilder.build( seasons, [], year, [] )

      if not priors:
         return None

      latest = priors[ Position.FIRST ]
      target_age = latest.age_in_year( year )

      def lookup( from_age: int, to_age: int ) -> ProductionCoefficient:
         return ProductionHistoryPredictor.coefficient( model.coefficients, from_age, to_age )

      return ProductionHistoryPredictor.pace(
         [ ( int( prior.age ), float( prior.pim_pace ), prior.games ) for prior in priors ],
         target_age,
         lookup )
