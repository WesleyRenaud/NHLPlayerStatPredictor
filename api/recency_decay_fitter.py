from __future__ import annotations

from .nhl_skater_season import NhlSkaterSeason
from .recency_weight import RecencyWeight
from .skater_season_years import SkaterSeasonYears


class RecencyDecayFitter():
   WINDOW = 4
   GRID_STEPS = 20


   @classmethod
   def fit( cls, seasons: list[ NhlSkaterSeason ] ) -> float:
      by_player = SkaterSeasonYears.by_player( seasons )
      best_decay = 0.0
      best_error: float | None = None

      for step in range( RecencyDecayFitter.GRID_STEPS + 1 ):
         decay = step / RecencyDecayFitter.GRID_STEPS
         error = cls._squared_error( by_player, decay )

         if best_error is None or error < best_error:
            best_decay = decay
            best_error = error

      return best_decay


   @classmethod
   def weights( cls, decay: float ) -> list[ RecencyWeight ]:
      raw = [
         decay ** lag
         for lag in range( RecencyDecayFitter.WINDOW )
      ]
      total = sum( raw )
      return [
         RecencyWeight( lag=lag, weight=raw[ lag ] / total )
         for lag in range( RecencyDecayFitter.WINDOW )
      ]


   @classmethod
   def _squared_error(
         cls,
         by_player: dict[ int, dict[ int, NhlSkaterSeason ] ],
         decay: float ) -> float:
      error = 0.0

      for years in by_player.values():
         for year, current in years.items():
            goals_total = 0.0
            assists_total = 0.0
            total = 0.0

            for lag in range( RecencyDecayFitter.WINDOW ):
               prior = years.get( year - lag - 1 )

               if prior is None:
                  continue

               weight = decay ** lag
               goals_total += prior.g_pace * weight
               assists_total += prior.a_pace * weight
               total += weight

            if total == 0:
               continue

            predicted_goals = goals_total / total
            predicted_assists = assists_total / total
            error += ( current.g_pace - predicted_goals ) ** 2
            error += ( current.a_pace - predicted_assists ) ** 2

      return error
