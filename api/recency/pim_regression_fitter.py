from __future__ import annotations

from collections import defaultdict

from .pim_regression_model import PimRegressionModel
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from .production_coefficient_fitter import ProductionCoefficientFitter
from .production_pair import ProductionPair
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason


class PimRegressionFitter():
   @classmethod
   def fit( cls, seasons: list[ NhlSkaterSeason ] ) -> PimRegressionModel:
      by_player: dict[ int, list[ NhlSkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         by_player[ season.player_id ].append( season )

      pairs: list[ ProductionPair ] = []

      for current in seasons:
         if current.games_played < PriorYear.MIN_GAMES:
            continue

         year = Season.start_year( current.season_id )
         priors = PriorYearBuilder._qualified( by_player[ current.player_id ], [], year )

         for prior in priors:
            lag = year - prior.year

            if lag > PriorYearBuilder.WIDTH or prior.pim_pace is None:
               continue

            age = int( prior.age )
            pairs.append( ProductionPair(
               from_age=age,
               to_age=age + lag,
               prior_pace=prior.pim_pace,
               following_pace=current.penalty_minutes_pace(),
               games=float( min( prior.games, current.games_played ) ) ) )

      return PimRegressionModel( ProductionCoefficientFitter.fit( pairs ) )
