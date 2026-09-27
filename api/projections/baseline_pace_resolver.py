from __future__ import annotations

from ..aging.league_factor import LeagueFactor
from ..recency.pace_regression_model import PaceRegressionModel
from ..recency.pace_regression_predictor import PaceRegressionPredictor
from ..recency.prior_year_builder import PriorYearBuilder
from ..season import Season
from .season_pace import SeasonPace
from ..skaters.skater import Skater


class BaselinePaceResolver():
   @classmethod
   def resolve(
         cls,
         skater: Skater,
         target_season_id: int,
         league_factors: list[ LeagueFactor ],
         model: PaceRegressionModel ) -> SeasonPace | None:
      year = Season.start_year( target_season_id )
      return PaceRegressionPredictor.pace(
         model,
         PriorYearBuilder.build( skater.seasons, league_factors, year ),
         year )
