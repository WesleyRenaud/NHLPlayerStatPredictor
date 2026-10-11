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
   def one_year_multiplier(
         cls,
         coefficients: list[ ProductionGrowth ],
         age: int ) -> float:
      return cls.coefficient( coefficients, age, age + 1 ).multiplier


   @classmethod
   def pace(
         cls,
         history: list[ ProductionSeason ],
         target_age: int,
         lookup: Callable[ [ int, int ], ProductionGrowth ],
         weight_lookup: Callable[ [ int, int ], ProductionWeight ],
         trajectory: ProductionTrajectoryFit ) -> float:
      latest = history[ Position.FIRST ]
      growth = cls.multiplier( lookup, latest.age, target_age )
      levels = [ cls._at_target_age( season, growth ) for season in history ]
      shares = ProductionTrajectory.shares(
         history,
         cls._weights( history, target_age, weight_lookup ),
         trajectory )
      return cls._blend( levels, shares )


   @classmethod
   def _at_target_age( cls, season: ProductionSeason, growth: float ) -> float:
      if season.arrival is not None:
         return season.arrival

      return season.pace * growth


   @classmethod
   def _weights(
         cls,
         history: list[ ProductionSeason ],
         target_age: int,
         weight_lookup: Callable[ [ int, int ], ProductionWeight ] ) -> list[ float ]:
      return [
         weight_lookup( season.age, target_age ).weight * PriorYear.reliability( season.games )
         for season in history
      ]


   @classmethod
   def _blend( cls, levels: list[ float ], shares: list[ float ] ) -> float:
      total = sum( shares )

      if not total:
         return max( 0.0, levels[ Position.FIRST ] )

      weighted = sum(
         share * level
         for share, level in zip( shares, levels, strict=True ) )
      return max( 0.0, weighted / total )
