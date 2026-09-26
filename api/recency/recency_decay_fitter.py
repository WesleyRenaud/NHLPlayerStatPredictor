from __future__ import annotations

from collections import defaultdict

from .age_recency_weights import AgeRecencyWeights
from .prior_season_weight_fitter import PriorSeasonWeightFitter
from .recency_weight import RecencyWeight
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.skater_season_years import SkaterSeasonYears


class RecencyDecayFitter():
   WINDOW = 4


   @classmethod
   def fit( cls, seasons: list[ NhlSkaterSeason ] ) -> list[ AgeRecencyWeights ]:
      return [
         AgeRecencyWeights( age, cls._weights( rows ) )
         for age, rows in sorted( cls._by_age( seasons ).items() )
      ]


   @classmethod
   def _weights(
         cls,
         rows: list[ tuple[ NhlSkaterSeason, list[ NhlSkaterSeason ] ] ]
         ) -> list[ RecencyWeight ]:
      max_width = max( len( priors ) for _current, priors in rows )

      for width in range( max_width, 0, -1 ):
         complete = [
            ( current, priors )
            for current, priors in rows
            if len( priors ) >= width
         ]

         if len( complete ) < width:
            continue

         samples: list[ list[ float ] ] = []

         for current, priors in complete:
            used = priors[ :width ]
            samples.append(
               [ current.g_pace, *[ prior.g_pace for prior in used ] ] )
            samples.append(
               [ current.a_pace, *[ prior.a_pace for prior in used ] ] )

         try:
            return cls._padded( PriorSeasonWeightFitter.fit( samples ) )
         except ZeroDivisionError:
            continue

      return cls._padded( [ RecencyWeight( 0, 1.0 ) ] )


   @classmethod
   def _padded( cls, weights: list[ RecencyWeight ] ) -> list[ RecencyWeight ]:
      by_lag = { weight.lag: weight.weight for weight in weights }
      return [
         RecencyWeight( lag, by_lag.get( lag, 0.0 ) )
         for lag in range( RecencyDecayFitter.WINDOW )
      ]


   @classmethod
   def _by_age(
         cls,
         seasons: list[ NhlSkaterSeason ]
         ) -> dict[ int, list[ tuple[ NhlSkaterSeason, list[ NhlSkaterSeason ] ] ] ]:
      grouped: dict[
         int,
         list[ tuple[ NhlSkaterSeason, list[ NhlSkaterSeason ] ] ]
      ] = defaultdict( list )

      for player_seasons in SkaterSeasonYears.by_player( seasons ).values():
         for current in player_seasons:
            priors = cls._priors( player_seasons, current )

            if not priors:
               continue

            grouped[ current.completed_age() ].append( ( current, priors ) )

      return grouped


   @classmethod
   def _priors(
         cls,
         seasons: list[ NhlSkaterSeason ],
         current: NhlSkaterSeason ) -> list[ NhlSkaterSeason ]:
      priors: list[ NhlSkaterSeason ] = []
      year = Season.start_year( current.season_id )

      for lag in range( RecencyDecayFitter.WINDOW ):
         prior = SkaterSeasonYears.at_year( seasons, year - lag - 1 )

         if prior is None:
            return priors

         priors.append( prior )

      return priors
