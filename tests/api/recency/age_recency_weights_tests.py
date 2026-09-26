from __future__ import annotations

from api.recency.age_recency_weights import AgeRecencyWeights
from api.recency.recency_weight import RecencyWeight


def _mix( last_year: float, previous: float ) -> list[ RecencyWeight ]:
   return [
      RecencyWeight( 0, last_year ),
      RecencyWeight( 1, previous ),
      RecencyWeight( 2, 0.0 ),
      RecencyWeight( 3, 0.0 ),
   ]


def Test_FromRow_TestPayload_ExpectAgeAndWeights() -> None:
   last_year = 1.0
   row = AgeRecencyWeights( 19, _mix( last_year, 0.0 ) ).to_dict()

   loaded = AgeRecencyWeights.from_row( row )

   assert loaded == AgeRecencyWeights( 19, _mix( last_year, 0.0 ) )


def Test_ForAge_TestExactAge_ExpectThatMix() -> None:
   nineteen = AgeRecencyWeights( 19, _mix( 1.0, 0.0 ) )
   twenty_eight = AgeRecencyWeights( 28, _mix( 0.5, 0.5 ) )

   weights = AgeRecencyWeights.for_age( [ nineteen, twenty_eight ], 28 )

   assert weights == twenty_eight.weights


def Test_ForAge_TestMissingAge_ExpectClosestMix() -> None:
   nineteen = AgeRecencyWeights( 19, _mix( 1.0, 0.0 ) )
   twenty_eight = AgeRecencyWeights( 28, _mix( 0.5, 0.5 ) )

   weights = AgeRecencyWeights.for_age( [ nineteen, twenty_eight ], 20 )

   assert weights == nineteen.weights
