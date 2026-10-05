from __future__ import annotations

from collections.abc import Callable

from .prior_year import PriorYear
from .production_growth import ProductionGrowth
from .production_season import ProductionSeason
from .production_trajectory import ProductionTrajectory
from .production_trajectory_fit import ProductionTrajectoryFit
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
         history: list[ ProductionSeason ],
         target_age: int,
         lookup: Callable[ [ int, int ], ProductionGrowth ],
         weight_lookup: Callable[ [ int, int ], ProductionWeight ],
         trajectory: ProductionTrajectoryFit ) -> float:
      bases = [
         weight_lookup( season.age, target_age ).weight * PriorYear.reliability( season.games )
         for season in history
      ]
      shares = ProductionTrajectory.shares( history, bases, trajectory )
      latest = history[ Position.FIRST ]
      weighted = 0.0
      total_weight = 0.0

      for season, share in zip( history, shares, strict=True ):
         # Qualified seasons are equally reliable regardless of league schedule length.
         weighted += share * season.pace
         total_weight += share

      # Average raw production first, then grow once from the latest season's age.
      average = weighted / total_weight if total_weight else latest.pace
      return max( 0.0, average * cls.multiplier( lookup, latest.age, target_age ) )
