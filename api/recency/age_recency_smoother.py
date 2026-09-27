from __future__ import annotations

from .age_recency_fit import AgeRecencyFit
from .age_recency_weights import AgeRecencyWeights
from .recency_weight import RecencyWeight
from ..shared.enums.position import Position


class AgeRecencySmoother():
   FIRST_AGE = 19
   SMOOTH_AGES = 3
   RATE_STEPS = 1000


   @classmethod
   def smooth( cls, rows: list[ AgeRecencyFit ] ) -> list[ AgeRecencyWeights ]:
      rates = {
         row.age: cls._rate( row.weights )
         for row in rows
         if row.age >= AgeRecencySmoother.FIRST_AGE
      }

      if not rates:
         return [ row.row() for row in rows ]

      window = len( rows[ Position.FIRST ].weights )
      by_age = { row.age: row for row in rows }
      smoothed: list[ AgeRecencyWeights ] = []

      for age in range( min( rates ), max( rates ) + 1 ):
         rate = cls._smoothed_rate( age, rates, by_age )

         if rate is None:
            continue

         smoothed.append(
            AgeRecencyWeights( age, cls._geometric( rate, window ) ) )

      return smoothed


   @classmethod
   def _smoothed_rate(
         cls,
         age: int,
         rates: dict[ int, float ],
         by_age: dict[ int, AgeRecencyFit ] ) -> float | None:
      total = 0.0
      weight = 0.0
      half = AgeRecencySmoother.SMOOTH_AGES // 2

      for neighbor in range( age - half, age + half + 1 ):
         if neighbor not in rates:
            continue

         samples = by_age[ neighbor ].samples
         total += rates[ neighbor ] * samples
         weight += samples

      if not weight:
         return None

      return total / weight


   @classmethod
   def _rate( cls, mix: list[ RecencyWeight ] ) -> float:
      best_error = None
      best_rate = 0.0

      for step in range( AgeRecencySmoother.RATE_STEPS + 1 ):
         rate = step / AgeRecencySmoother.RATE_STEPS
         error = cls._error( mix, rate )

         if best_error is None or error < best_error:
            best_error = error
            best_rate = rate

      return best_rate


   @classmethod
   def _error( cls, mix: list[ RecencyWeight ], rate: float ) -> float:
      geometric = cls._geometric( rate, len( mix ) )
      return sum(
         ( left.weight - right.weight ) ** 2
         for left, right in zip( mix, geometric ) )


   @classmethod
   def _geometric( cls, rate: float, window: int ) -> list[ RecencyWeight ]:
      raw = [
         rate ** lag
         for lag in range( window )
      ]
      total = sum( raw )
      return [
         RecencyWeight( lag, value / total )
         for lag, value in enumerate( raw )
      ]
