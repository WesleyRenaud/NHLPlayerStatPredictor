from __future__ import annotations

from collections import defaultdict

from .age_recency_blender import AgeRecencyBlender
from .age_recency_weights import AgeRecencyWeights
from ..depth.usable_nhl_ice import UsableNhlIce
from .prior_season_weight_fitter import PriorSeasonWeightFitter
from .recency_weight import RecencyWeight
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.skater_season_years import SkaterSeasonYears


class RecencyDecayFitter():
   WINDOW = 4
   POOLED_AGE = 34


   @classmethod
   def fit( cls, seasons: list[ NhlSkaterSeason ] ) -> list[ AgeRecencyWeights ]:
      return AgeRecencyBlender.blend(
         [
            AgeRecencyWeights( age, cls._weights( rows ) )
            for age, rows in sorted( cls._by_age( seasons ).items() )
         ],
         RecencyDecayFitter.POOLED_AGE )


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
            if not cls._enough_games( current ):
               continue

            priors = cls._priors( player_seasons, current )

            if not priors:
               continue

            grouped[ cls._age( current ) ].append( ( current, priors ) )

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

         if prior is None or not cls._enough_games( prior ):
            return priors

         priors.append( prior )

      return priors


   @classmethod
   def _age( cls, season: NhlSkaterSeason ) -> int:
      age = season.completed_age()

      if age < RecencyDecayFitter.POOLED_AGE:
         return age

      return RecencyDecayFitter.POOLED_AGE


   @classmethod
   def _enough_games( cls, season: NhlSkaterSeason ) -> bool:
      return season.games_played >= UsableNhlIce.MIN_GAMES
