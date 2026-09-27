from __future__ import annotations

from api.recency.age_recency_blender import AgeRecencyBlender
from api.recency.age_recency_weights import AgeRecencyWeights
from api.recency.recency_weight import RecencyWeight
from api.shared.enums.position import Position


def _first_weight_one() -> list[ RecencyWeight ]:
   return [
      RecencyWeight( lag, 1.0 if lag == Position.FIRST else 0.0 )
      for lag in range( 4 )
   ]


def _equal_weights() -> list[ RecencyWeight ]:
   weight = 1.0 / 4
   return [
      RecencyWeight( lag, weight )
      for lag in range( 4 )
   ]


def Test_Blend_TestAfterPooled_ExpectPooledMix() -> None:
   early_mix = AgeRecencyWeights( 32, _first_weight_one() )
   pooled_mix = AgeRecencyWeights( 34, _equal_weights() )

   rows = AgeRecencyBlender.blend( [ early_mix, pooled_mix ], 34 )

   assert next(
      row for row in rows if row.age == AgeRecencyBlender.LAST_AGE
   ) == AgeRecencyWeights( AgeRecencyBlender.LAST_AGE, _equal_weights() )


def Test_Blend_TestPooledAge_ExpectUnchanged() -> None:
   pooled_mix = AgeRecencyWeights( 34, _equal_weights() )

   rows = AgeRecencyBlender.blend( [ pooled_mix ], 34 )

   assert next( row for row in rows if row.age == 34 ) == pooled_mix


def Test_Blend_TestYoungerAge_ExpectKept() -> None:
   early_mix = AgeRecencyWeights( 32, _first_weight_one() )
   pooled_mix = AgeRecencyWeights( 34, _equal_weights() )

   rows = AgeRecencyBlender.blend( [ early_mix, pooled_mix ], 34 )

   assert next( row for row in rows if row.age == 32 ) == early_mix


def Test_Blend_TestMissingPooled_ExpectUnchanged() -> None:
   early_mix = AgeRecencyWeights( 32, _first_weight_one() )

   rows = AgeRecencyBlender.blend( [ early_mix ], 34 )

   assert rows == [ early_mix ]
