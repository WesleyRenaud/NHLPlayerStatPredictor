from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from functools import partial

from .production_growth import ProductionGrowth
from .production_history_predictor import ProductionHistoryPredictor
from .production_keep_fit import ProductionKeepFit
from .production_keep_sample import ProductionKeepSample
from .production_trend import ProductionTrend
from .production_trend_line import ProductionTrendLine
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason


class ProductionKeepFitter():
   @classmethod
   def fit( cls, samples: list[ ProductionKeepSample ] ) -> ProductionKeepFit:
      """Share of the latest season's gap from the line still present the next season."""
      share = cls._share( samples )

      if share is None:
         return ProductionKeepFit.empty()

      return ProductionKeepFit( kept_above=share )


   @classmethod
   def observe(
         cls,
         seasons: list[ NhlSkaterSeason ],
         growth: list[ ProductionGrowth ] ) -> list[ ProductionKeepSample ]:
      lookup = partial( ProductionHistoryPredictor.coefficient, growth )
      by_player: dict[ int, list[ NhlSkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         by_player[ season.player_id ].append( season )

      samples: list[ ProductionKeepSample ] = []

      for player_seasons in by_player.values():
         samples.extend( cls._windows( player_seasons, lookup ) )

      return samples


   @classmethod
   def _windows(
         cls,
         seasons: list[ NhlSkaterSeason ],
         lookup: Callable[ [ int, int ], ProductionGrowth ] ) -> list[ ProductionKeepSample ]:
      by_year: dict[ int, list[ NhlSkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         by_year[ Season.start_year( season.season_id ) ].append( season )

      if not by_year:
         return []

      first = min( by_year )
      last = max( by_year )
      samples: list[ ProductionKeepSample ] = []

      for following_year in range( first, last + 1 ):
         sample = cls._sample( by_year, following_year, lookup )

         if sample is not None:
            samples.append( sample )

      return samples


   @classmethod
   def _sample(
         cls,
         by_year: dict[ int, list[ NhlSkaterSeason ] ],
         following_year: int,
         lookup: Callable[ [ int, int ], ProductionGrowth ] ) -> ProductionKeepSample | None:
      latest_year = following_year - 1
      oldest_year = latest_year - ProductionTrend.PRIOR_SEASONS
      priors: list[ NhlSkaterSeason ] = []

      for year in range( oldest_year, latest_year ):
         season = ProductionTrend.full_season( by_year.get( year, [] ) )

         if season is None:
            return None

         priors.append( season )

      latest = ProductionTrend.full_season( by_year.get( latest_year, [] ) )
      following = ProductionTrend.full_season( by_year.get( following_year, [] ) )

      if latest is None or following is None:
         return None

      line = ProductionTrendLine.fit( [ season.p_pace for season in priors ] )
      multiplier = ProductionHistoryPredictor.multiplier( lookup, latest.age, following.age )

      if multiplier <= 0.0:
         return None

      return ProductionKeepSample(
         line.level,
         latest.p_pace,
         following.p_pace / multiplier,
         min( latest.games_played, following.games_played ) )


   @classmethod
   def _share( cls, samples: list[ ProductionKeepSample ] ) -> float | None:
      numerator = 0.0
      denominator = 0.0

      for sample in samples:
         gap = sample.latest_pace - sample.level

         if gap == 0.0:
            continue

         numerator += sample.games * ( sample.adjusted_following - sample.level ) * gap
         denominator += sample.games * gap * gap

      if denominator == 0.0:
         return None

      return cls._bounded( numerator / denominator )


   @classmethod
   def _bounded( cls, share: float ) -> float:
      return min( 1.0, max( 0.0, share ) )
