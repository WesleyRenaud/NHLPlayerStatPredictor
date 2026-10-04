from __future__ import annotations

from ..aging.league_factor import LeagueFactor
from ..depth.nhl_player_season_ice_scale import NhlPlayerSeasonIceScale
from .pace_values import PaceValues
from ..recency.pace_regression_model import PaceRegressionModel
from ..recency.pace_regression_predictor import PaceRegressionPredictor
from ..recency.prior_year_builder import PriorYearBuilder
from ..season import Season
from ..skaters.skater import Skater


class BaselinePaceResolver():
   @classmethod
   def resolve(
         cls,
         skater: Skater,
         target_season_id: int,
         league_factors: list[ LeagueFactor ],
         model: PaceRegressionModel,
         player_ice_scales: list[ NhlPlayerSeasonIceScale ] | None = None ) -> PaceValues | None:
      year = Season.start_year( target_season_id )
      return PaceRegressionPredictor.paces(
         model,
         PriorYearBuilder.build( skater.seasons, league_factors, year, model.component_shares, player_ice_scales ),
         target_season_id,
         skater.nhl_seasons(),
         player_ice_scales )
