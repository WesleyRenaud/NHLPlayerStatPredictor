from __future__ import annotations

from .aging_factor import AgingFactor
from .aging_pair_totals import AgingPairTotals
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.other_league_season_years import OtherLeagueSeasonYears
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_season import SkaterSeason
from ..skaters.skater_season_years import SkaterSeasonYears


class AgingCurveFitter():
   LAST_AGE = 40
   SMOOTH_AGES = 3


   @classmethod
   def fit(
         cls,
         seasons: list[ NhlSkaterSeason ],
         other_seasons: list[ OtherLeagueSkaterSeason ] ) -> list[ AgingFactor ]:
      pair_counts, goal_percents, assist_percents = cls._percents_by_age(
         seasons,
         other_seasons )
      return cls._smoothed( pair_counts, goal_percents, assist_percents )


   @classmethod
   def _percents_by_age(
         cls,
         seasons: list[ NhlSkaterSeason ],
         other_seasons: list[ OtherLeagueSkaterSeason ] ) -> tuple[
            dict[ int, int ],
            dict[ int, float ],
            dict[ int, float ] ]:
      totals_by_age: dict[ int, AgingPairTotals ] = {}

      for current, following in SkaterSeasonYears.consecutive( seasons ):
         cls._add_pair( totals_by_age, current, following )

      for current, following in OtherLeagueSeasonYears.consecutive( other_seasons ):
         cls._add_pair( totals_by_age, current, following )

      goal_percents: dict[ int, float ] = {}
      assist_percents: dict[ int, float ] = {}
      counted: dict[ int, int ] = {}

      for age, totals in totals_by_age.items():
         percent = totals.percent()

         if percent is None:
            continue

         counted[ age ] = totals.pair_count
         goal_percents[ age ], assist_percents[ age ] = percent

      return counted, goal_percents, assist_percents


   @classmethod
   def _add_pair(
         cls,
         totals_by_age: dict[ int, AgingPairTotals ],
         current: SkaterSeason,
         following: SkaterSeason ) -> None:
      age = current.completed_age()

      if age > AgingCurveFitter.LAST_AGE:
         return

      totals = totals_by_age.get( age, AgingPairTotals.empty() )
      totals_by_age[ age ] = totals.adding( current, following )


   @classmethod
   def _smoothed(
         cls,
         pair_counts: dict[ int, int ],
         goal_percents: dict[ int, float ],
         assist_percents: dict[ int, float ] ) -> list[ AgingFactor ]:
      return [
         cls._smoothed_factor( age, pair_counts, goal_percents, assist_percents )
         for age in sorted( pair_counts )
      ]


   @classmethod
   def _smoothed_factor(
         cls,
         age: int,
         pair_counts: dict[ int, int ],
         goal_percents: dict[ int, float ],
         assist_percents: dict[ int, float ] ) -> AgingFactor:
      total_pairs = 0
      goals = 0.0
      assists = 0.0

      for neighbor_age in cls._neighbor_ages( age ):
         if neighbor_age not in pair_counts:
            continue

         pair_count = pair_counts[ neighbor_age ]
         total_pairs += pair_count
         goals += pair_count * goal_percents[ neighbor_age ]
         assists += pair_count * assist_percents[ neighbor_age ]

      return AgingFactor(
         age=age,
         goals=goals / total_pairs,
         assists=assists / total_pairs )


   @classmethod
   def _neighbor_ages( cls, age: int ) -> range:
      half = AgingCurveFitter.SMOOTH_AGES // 2
      return range( age - half, age + half + 1 )
