from __future__ import annotations

from .age_recency_weights import AgeRecencyWeights
from .recency_weight import RecencyWeight


class AgeRecencyBlender():
   EARLY_AGE = 32
   LAST_AGE = 40


   @classmethod
   def blend(
         cls,
         rows: list[ AgeRecencyWeights ],
         pooled_age: int ) -> list[ AgeRecencyWeights ]:
      pooled_mix = { row.age: row for row in rows }.get( pooled_age )

      if pooled_mix is None:
         return rows

      kept = [ row for row in rows if row.age <= AgeRecencyBlender.EARLY_AGE ]
      early_weights = pooled_mix.weights

      if kept:
         early_weights = AgeRecencyWeights.for_age(
            kept,
            AgeRecencyBlender.EARLY_AGE )

      span = AgeRecencyBlender.LAST_AGE - AgeRecencyBlender.EARLY_AGE
      blended = [
         AgeRecencyWeights(
            age,
            cls._lerp(
               early_weights,
               pooled_mix.weights,
               ( age - AgeRecencyBlender.EARLY_AGE ) / span ) )
         for age in range(
            AgeRecencyBlender.EARLY_AGE + 1,
            AgeRecencyBlender.LAST_AGE + 1 )
      ]
      return [ *kept, *blended ]


   @classmethod
   def _lerp(
         cls,
         early_weights: list[ RecencyWeight ],
         pooled_weights: list[ RecencyWeight ],
         share: float ) -> list[ RecencyWeight ]:
      return [
         RecencyWeight(
            lag=left.lag,
            weight=( 1.0 - share ) * left.weight + share * right.weight )
         for left, right in zip( early_weights, pooled_weights )
      ]
