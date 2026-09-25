from __future__ import annotations

from .prior_season_weight_fitter import PriorSeasonWeightFitter
from .recency_weight import RecencyWeight
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.skater_season_years import SkaterSeasonYears


class RecencyDecayFitter():
   WINDOW = 4


   @classmethod
   def fit( cls, seasons: list[ NhlSkaterSeason ] ) -> list[ RecencyWeight ]:
      return PriorSeasonWeightFitter.fit( cls._samples( seasons ) )


   @classmethod
   def _samples( cls, seasons: list[ NhlSkaterSeason ] ) -> list[ list[ float ] ]:
      samples: list[ list[ float ] ] = []

      for player_seasons in SkaterSeasonYears.by_player( seasons ).values():
         for current in player_seasons:
            samples.extend( cls._year_samples( player_seasons, current ) )

      return samples


   @classmethod
   def _year_samples(
         cls,
         seasons: list[ NhlSkaterSeason ],
         current: NhlSkaterSeason ) -> list[ list[ float ] ]:
      goals: list[ float ] = []
      assists: list[ float ] = []
      year = Season.start_year( current.season_id )

      for lag in range( RecencyDecayFitter.WINDOW ):
         prior = SkaterSeasonYears.at_year( seasons, year - lag - 1 )

         if prior is None:
            return []

         goals.append( prior.g_pace )
         assists.append( prior.a_pace )

      return [
         [ current.g_pace, *goals ],
         [ current.a_pace, *assists ],
      ]
