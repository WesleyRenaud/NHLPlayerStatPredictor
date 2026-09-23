from __future__ import annotations

from .nhl_skater_season import NhlSkaterSeason
from .prior_season_weight_fitter import PriorSeasonWeightFitter
from .recency_weight import RecencyWeight
from .season import Season
from .skater_season_years import SkaterSeasonYears


class AvailabilityDecayFitter():
   WINDOW = 6


   @classmethod
   def fit( cls, seasons: list[ NhlSkaterSeason ] ) -> list[ RecencyWeight ]:
      return PriorSeasonWeightFitter.fit( cls._samples( seasons ) )


   @classmethod
   def _samples( cls, seasons: list[ NhlSkaterSeason ] ) -> list[ list[ float ] ]:
      samples: list[ list[ float ] ] = []

      for player_seasons in SkaterSeasonYears.by_player( seasons ).values():
         for current in player_seasons:
            sample = cls._sample( player_seasons, current )

            if sample is not None:
               samples.append( sample )

      return samples


   @classmethod
   def _sample(
         cls,
         seasons: list[ NhlSkaterSeason ],
         current: NhlSkaterSeason ) -> list[ float ] | None:
      if current.gp_share is None:
         return None

      priors: list[ float ] = []
      year = Season.start_year( current.season_id )

      for lag in range( AvailabilityDecayFitter.WINDOW ):
         prior = SkaterSeasonYears.at_year( seasons, year - lag - 1 )

         if prior is None or prior.gp_share is None:
            return None

         priors.append( prior.gp_share )

      return [ current.gp_share, *priors ]
