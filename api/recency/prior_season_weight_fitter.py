from __future__ import annotations

from .linear_system import LinearSystem
from .recency_weight import RecencyWeight
from ..shared.enums.position import Position


class PriorSeasonWeightFitter():
   @classmethod
   def fit( cls, samples: list[ list[ float ] ] ) -> list[ RecencyWeight ]:
      window = len( samples[ Position.FIRST ] ) - 1
      coefficients = [
         max( value, 0.0 )
         for value in cls._coefficients( samples, window )
      ]
      total = sum( coefficients )

      if not total:
         return [
            RecencyWeight(
               lag=years_ago,
               weight=1.0 if years_ago == Position.FIRST else 0.0 )
            for years_ago in range( window )
         ]

      return [
         RecencyWeight( lag=years_ago, weight=coefficients[ years_ago ] / total )
         for years_ago in range( window )
      ]


   @classmethod
   def _coefficients(
         cls,
         samples: list[ list[ float ] ],
         window: int ) -> list[ float ]:
      products = [
         [ 0.0 ] * window
         for _ in range( window )
      ]
      targets = [ 0.0 ] * window

      for sample in samples:
         current = sample[ Position.FIRST ]
         priors = sample[ Position.SECOND: ]

         for years_ago in range( window ):
            targets[ years_ago ] += priors[ years_ago ] * current

            for other in range( window ):
               products[ years_ago ][ other ] += priors[ years_ago ] * priors[ other ]

      return LinearSystem.solve( products, targets )
