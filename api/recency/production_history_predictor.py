from __future__ import annotations

from collections.abc import Callable

from .production_coefficient import ProductionCoefficient
from ..shared.enums.position import Position


class ProductionHistoryPredictor():
   @classmethod
   def coefficient(
         cls,
         coefficients: list[ ProductionCoefficient ],
         from_age: int,
         to_age: int ) -> ProductionCoefficient:
      matching = [
         coefficient for coefficient in coefficients
         if coefficient.to_age - coefficient.from_age == to_age - from_age
      ]

      if not matching:
         return ProductionCoefficient( from_age, to_age, 1.0, 0.0, 0 )

      return min( matching, key=lambda coefficient: abs( coefficient.from_age - from_age ) )


   @classmethod
   def multiplier(
         cls,
         lookup: Callable[ [ int, int ], ProductionCoefficient ],
         from_age: int,
         to_age: int ) -> float:
      multiplier = 1.0

      for age in range( from_age, to_age ):
         multiplier *= lookup( age, age + 1 ).multiplier

      return multiplier


   @classmethod
   def pace(
         cls,
         history: list[ tuple[ int, float, int ] ],
         target_age: int,
         lookup: Callable[ [ int, int ], ProductionCoefficient ] ) -> float:
      anchor_age = history[ Position.FIRST ][ 0 ]
      weighted = 0.0
      total_weight = 0.0

      for age, value, games in history:
         weight = lookup( age, target_age ).weight * games
         weighted += weight * value * cls.multiplier( lookup, age, anchor_age )
         total_weight += weight

      average = history[ Position.FIRST ][ 1 ] if not total_weight else weighted / total_weight
      return max( 0.0, average * cls.multiplier( lookup, anchor_age, target_age ) )
