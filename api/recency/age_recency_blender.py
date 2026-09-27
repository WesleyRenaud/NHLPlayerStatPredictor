from __future__ import annotations

from .age_recency_weights import AgeRecencyWeights


class AgeRecencyBlender():
   LAST_AGE = 40


   @classmethod
   def blend(
         cls,
         rows: list[ AgeRecencyWeights ],
         pooled_age: int ) -> list[ AgeRecencyWeights ]:
      pooled_mix = { row.age: row for row in rows }.get( pooled_age )

      if pooled_mix is None:
         return rows

      kept = [ row for row in rows if row.age <= pooled_age ]
      return [
         *kept,
         *[
            AgeRecencyWeights( age, pooled_mix.weights )
            for age in range( pooled_age + 1, AgeRecencyBlender.LAST_AGE + 1 )
         ]
      ]
