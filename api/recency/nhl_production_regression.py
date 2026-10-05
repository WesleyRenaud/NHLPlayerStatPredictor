from __future__ import annotations

from collections import defaultdict
from functools import partial

from .nhl_production_stat import NhlProductionStat
from .prior_year import PriorYear
from .prior_year_builder import PriorYearBuilder
from .production_coefficient import ProductionCoefficient
from .production_coefficient_fitter import ProductionCoefficientFitter
from .production_growth import ProductionGrowth
from .production_history_predictor import ProductionHistoryPredictor
from .production_pair import ProductionPair
from .production_season import ProductionSeason
from .production_trajectory_fit import ProductionTrajectoryFit
from .production_weight import ProductionWeight
from ..season import Season
from ..shared.enums.position import Position
from ..skaters.nhl_skater_season import NhlSkaterSeason


class NhlProductionRegression():
   @classmethod
   def fit(
         cls,
         seasons: list[ NhlSkaterSeason ],
         stat: NhlProductionStat,
         history_by_player: dict[ int, list[ PriorYear ] ] | None = None ) -> list[ ProductionCoefficient ]:
      if history_by_player is None:
         history_by_player = cls.history( seasons )

      samples: list[ ProductionPair ] = []

      for current in seasons:
         if current.games_played < PriorYear.MIN_GAMES:
            continue

         year = Season.start_year( current.season_id )
         actual = (
            current.penalty_minutes_pace() if stat == NhlProductionStat.PIM
            else current.shots_pace() )

         for prior in history_by_player[ current.player_id ]:
            lag = year - prior.year

            if prior.games < PriorYear.MIN_GAMES or not 0 < lag <= PriorYearBuilder.WIDTH:
               continue

            age = int( prior.age )
            samples.append( ProductionPair(
               from_age=age,
               to_age=age + lag,
               prior_pace=getattr( prior, stat.value ),
               following_pace=actual,
               games=float( min( prior.games, current.games_played ) ) ) )

      return ProductionCoefficientFitter.fit( samples )


   @classmethod
   def history( cls, seasons: list[ NhlSkaterSeason ] ) -> dict[ int, list[ PriorYear ] ]:
      by_player: dict[ int, list[ NhlSkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         by_player[ season.player_id ].append( season )

      return {
         player_id: PriorYearBuilder.history( history, [], [] )
         for player_id, history in by_player.items()
      }


   @classmethod
   def pace(
         cls,
         coefficients: list[ ProductionCoefficient ],
         priors: list[ PriorYear ],
         year: int,
         stat: NhlProductionStat,
         trajectory: ProductionTrajectoryFit ) -> float | None:
      if not priors:
         return None

      target_age = priors[ Position.FIRST ].age_in_year( year )

      growth = [ ProductionGrowth( coefficient.from_age, coefficient.to_age,
         coefficient.multiplier, coefficient.samples ) for coefficient in coefficients ]
      weights = [ ProductionWeight( coefficient.from_age, coefficient.to_age,
         coefficient.weight, coefficient.samples ) for coefficient in coefficients ]

      return ProductionHistoryPredictor.pace(
         [ ProductionSeason( int( prior.age ), getattr( prior, stat.value ), prior.games ) for prior in priors ],
         target_age,
         partial( ProductionHistoryPredictor.coefficient, growth ),
         partial( ProductionHistoryPredictor.weight, weights ),
         trajectory )
