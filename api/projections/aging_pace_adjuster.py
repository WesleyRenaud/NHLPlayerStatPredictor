from __future__ import annotations

from ..aging_factor import AgingFactor
from .career_pace import CareerPace
from ..shared.enums.position import Position


class AgingPaceAdjuster():
   @classmethod
   def adjust(
         cls,
         pace: CareerPace,
         age: int,
         factors: list[ AgingFactor ] ) -> CareerPace:
      factor = cls._factor_for( age, factors )
      return CareerPace(
         goals=pace.goals * ( 1.0 + factor.goals ),
         assists=pace.assists * ( 1.0 + factor.assists ) )


   @classmethod
   def _factor_for( cls, age: int, factors: list[ AgingFactor ] ) -> AgingFactor:
      closest = factors[ Position.FIRST ]

      for factor in factors:
         if abs( factor.age - age ) < abs( closest.age - age ):
            closest = factor

      return closest
