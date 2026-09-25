from __future__ import annotations

from ..aging.aging_pair_totals import AgingPairTotals
from .player_aging_rate import PlayerAgingRate
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.skater_season_years import SkaterSeasonYears


class PlayerAgingFitter():
   WINDOW = 4


   @classmethod
   def fit( cls, seasons: list[ NhlSkaterSeason ] ) -> PlayerAgingRate | None:
      totals = AgingPairTotals.empty()
      pairs = SkaterSeasonYears.consecutive( seasons )[ -PlayerAgingFitter.WINDOW: ]

      for current, following in pairs:
         totals = totals.adding( current, following )

      percent = totals.percent()

      if percent is None:
         return None

      goals, assists = percent
      return PlayerAgingRate( totals.pair_count, goals, assists )
