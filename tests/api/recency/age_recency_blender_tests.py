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


def Test_Blend_TestMidSpan_ExpectHalfway() -> None:
   early_mix = AgeRecencyWeights( AgeRecencyBlender.EARLY_AGE, _first_weight_one() )
   pooled_mix = AgeRecencyWeights( 34, _equal_weights() )

   rows = AgeRecencyBlender.blend( [ early_mix, pooled_mix ], 34 )

   mid_age = ( AgeRecencyBlender.EARLY_AGE + AgeRecencyBlender.LAST_AGE ) // 2
   half = 0.5
   assert next( row for row in rows if row.age == mid_age ) == AgeRecencyWeights(
      mid_age,
      [
         RecencyWeight(
            lag,
            ( 1.0 - half ) * left.weight + half * right.weight )
         for lag, left, right in zip(
            range( 4 ),
            _first_weight_one(),
            _equal_weights() )
      ] )


def Test_Blend_TestLastAge_ExpectPooledMix() -> None:
   early_mix = AgeRecencyWeights( AgeRecencyBlender.EARLY_AGE, _first_weight_one() )
   pooled_mix = AgeRecencyWeights( 34, _equal_weights() )

   rows = AgeRecencyBlender.blend( [ early_mix, pooled_mix ], 34 )

   assert next(
      row for row in rows if row.age == AgeRecencyBlender.LAST_AGE
   ) == AgeRecencyWeights( AgeRecencyBlender.LAST_AGE, _equal_weights() )


def Test_Blend_TestThirtyThree_ExpectMostlyEarly() -> None:
   early_mix = AgeRecencyWeights( AgeRecencyBlender.EARLY_AGE, _first_weight_one() )
   pooled_mix = AgeRecencyWeights( 34, _equal_weights() )
   share = 1.0 / ( AgeRecencyBlender.LAST_AGE - AgeRecencyBlender.EARLY_AGE )

   rows = AgeRecencyBlender.blend( [ early_mix, pooled_mix ], 34 )

   assert next( row for row in rows if row.age == 33 ) == AgeRecencyWeights(
      33,
      [
         RecencyWeight(
            lag,
            ( 1.0 - share ) * left.weight + share * right.weight )
         for lag, left, right in zip(
            range( 4 ),
            _first_weight_one(),
            _equal_weights() )
      ] )


def Test_Blend_TestEarlyAge_ExpectUnchanged() -> None:
   early_mix = AgeRecencyWeights( AgeRecencyBlender.EARLY_AGE, _first_weight_one() )
   pooled_mix = AgeRecencyWeights( 34, _equal_weights() )

   rows = AgeRecencyBlender.blend( [ early_mix, pooled_mix ], 34 )

   assert next(
      row for row in rows if row.age == AgeRecencyBlender.EARLY_AGE
   ) == early_mix
