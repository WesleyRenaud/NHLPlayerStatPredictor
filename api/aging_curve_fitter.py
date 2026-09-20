from __future__ import annotations

from collections import defaultdict

from .aging_factor import AgingFactor
from .season import Season
from .skater_season import SkaterSeason


class AgingCurveFitter():
   SMOOTH_AGES = 3


   @classmethod
   def fit( cls, seasons: list[ SkaterSeason ] ) -> list[ AgingFactor ]:
      pair_counts, goal_percents, assist_percents = cls._percents_by_age( seasons )
      return cls._smoothed( pair_counts, goal_percents, assist_percents )


   @classmethod
   def _percents_by_age(
         cls,
         seasons: list[ SkaterSeason ] ) -> tuple[
            dict[ int, int ],
            dict[ int, float ],
            dict[ int, float ] ]:
      pair_counts: dict[ int, int ] = defaultdict( int )
      goal_pace: dict[ int, float ] = defaultdict( float )
      assist_pace: dict[ int, float ] = defaultdict( float )
      goal_change: dict[ int, float ] = defaultdict( float )
      assist_change: dict[ int, float ] = defaultdict( float )

      for age, current, following in cls._consecutive_seasons( seasons ):
         pair_counts[ age ] += 1
         goal_pace[ age ] += current.g_pace
         assist_pace[ age ] += current.a_pace
         goal_change[ age ] += following.g_pace - current.g_pace
         assist_change[ age ] += following.a_pace - current.a_pace

      goal_percents: dict[ int, float ] = {}
      assist_percents: dict[ int, float ] = {}
      counted: dict[ int, int ] = {}

      for age, pair_count in pair_counts.items():
         if goal_pace[ age ] == 0 or assist_pace[ age ] == 0:
            continue

         counted[ age ] = pair_count
         goal_percents[ age ] = goal_change[ age ] / goal_pace[ age ]
         assist_percents[ age ] = assist_change[ age ] / assist_pace[ age ]

      return counted, goal_percents, assist_percents


   @classmethod
   def _consecutive_seasons(
         cls,
         seasons: list[ SkaterSeason ] ) -> list[ tuple[ int, SkaterSeason, SkaterSeason ] ]:
      pairs: list[ tuple[ int, SkaterSeason, SkaterSeason ] ] = []

      for years in cls._years_by_player( seasons ).values():
         for year, current in years.items():
            following = years.get( year + 1 )

            if following is None:
               continue

            pairs.append( ( int( current.age ), current, following ) )

      return pairs


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


   @classmethod
   def _years_by_player(
         cls,
         seasons: list[ SkaterSeason ] ) -> dict[ int, dict[ int, SkaterSeason ] ]:
      by_player: dict[ int, dict[ int, SkaterSeason ] ] = {}

      for season in seasons:
         years = by_player.setdefault( season.player_id, {} )
         years[ Season.start_year( season.season_id ) ] = season

      return by_player
