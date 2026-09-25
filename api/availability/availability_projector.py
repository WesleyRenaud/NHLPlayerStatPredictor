from __future__ import annotations

from .games_share import GamesShare
from ..recency.recency_weight import RecencyWeight
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason


class AvailabilityProjector():
   @classmethod
   def resolve(
         cls,
         seasons: list[ NhlSkaterSeason ],
         weights: list[ RecencyWeight ],
         target_season_id: int ) -> float:
      by_lag = {
         Season.recency_lag( target_season_id, season.season_id ): season
         for season in seasons
         if season.gp_share is not None
      }
      total = 0.0
      share = 0.0

      for weight in weights:
         season = by_lag.get( weight.lag )

         if season is None:
            continue

         share += season.gp_share * weight.weight
         total += weight.weight

      if not total:
         return GamesShare.FULL

      return share / total
