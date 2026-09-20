from __future__ import annotations

from ..aging_factor import AgingFactor
from .career_pace import CareerPace
from .player_aging_fitter import PlayerAgingFitter
from ..shared.enums.position import Position
from ..skater_season import SkaterSeason


class AgingPaceAdjuster():
   SHRINK = 4


   @classmethod
   def adjust(
         cls,
         pace: CareerPace,
         age: int,
         factors: list[ AgingFactor ],
         seasons: list[ SkaterSeason ] ) -> CareerPace:
      league = cls._factor_for( age, factors )
      player_rate = PlayerAgingFitter.fit( seasons )

      if player_rate is None:
         return cls._scale( pace, league.goals, league.assists )

      weight = player_rate.pair_count / (
         player_rate.pair_count + AgingPaceAdjuster.SHRINK )
      return cls._scale(
         pace,
         cls._blend( weight, player_rate.goals, league.goals ),
         cls._blend( weight, player_rate.assists, league.assists ) )


   @classmethod
   def _scale( cls, pace: CareerPace, goals: float, assists: float ) -> CareerPace:
      return CareerPace(
         goals=pace.goals * ( 1.0 + goals ),
         assists=pace.assists * ( 1.0 + assists ) )


   @classmethod
   def _blend(
         cls,
         weight: float,
         player_percent: float,
         league_percent: float ) -> float:
      return weight * player_percent + ( 1.0 - weight ) * league_percent


   @classmethod
   def _factor_for( cls, age: int, factors: list[ AgingFactor ] ) -> AgingFactor:
      closest = factors[ Position.FIRST ]

      for factor in factors:
         if abs( factor.age - age ) < abs( closest.age - age ):
            closest = factor

      return closest
