from __future__ import annotations

from collections.abc import Callable

from .prior_year import PriorYear
from .production_growth import ProductionGrowth
from .production_weight import ProductionWeight
from ..shared.enums.position import Position


class ProductionHistoryPredictor():
   @classmethod
   def coefficient(
         cls,
         coefficients: list[ ProductionGrowth ],
         from_age: int,
         to_age: int ) -> ProductionGrowth:
      matching = [
         coefficient for coefficient in coefficients
         if coefficient.to_age - coefficient.from_age == to_age - from_age
      ]

      if not matching:
         return ProductionGrowth( from_age, to_age, 1.0, 0 )

      return min( matching, key=lambda coefficient: abs( coefficient.from_age - from_age ) )


   @classmethod
   def weight(
         cls,
         weights: list[ ProductionWeight ],
         from_age: int,
         to_age: int ) -> ProductionWeight:
      matching = [ weight for weight in weights if weight.to_age - weight.from_age == to_age - from_age ]

      if not matching:
         return ProductionWeight( from_age, to_age, 0.0, 0 )

      return min( matching, key=lambda weight: abs( weight.from_age - from_age ) )


   @classmethod
   def multiplier(
         cls,
         lookup: Callable[ [ int, int ], ProductionGrowth ],
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
         lookup: Callable[ [ int, int ], ProductionGrowth ],
         weight_lookup: Callable[ [ int, int ], ProductionWeight ] ) -> float:
      weighted = 0.0
      total_weight = 0.0

      for age, value, games in history:
         # Qualified seasons are equally reliable regardless of league schedule length.
         weight = weight_lookup( age, target_age ).weight * min( games, PriorYear.MIN_GAMES )
         weighted += weight * value
         total_weight += weight

      # Average raw production first, then grow once from the latest season's age.
      latest_age, latest_value, _ = history[ Position.FIRST ]
      average = weighted / total_weight if total_weight else latest_value
      return max( 0.0, average * cls.multiplier( lookup, latest_age, target_age ) )
