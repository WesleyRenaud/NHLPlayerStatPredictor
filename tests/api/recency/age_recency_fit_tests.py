from __future__ import annotations

from api.recency.age_recency_fit import AgeRecencyFit
from api.recency.age_recency_weights import AgeRecencyWeights
from api.recency.recency_weight import RecencyWeight


def Test_Row_TestFit_ExpectAgeAndWeights() -> None:
   mix = [ RecencyWeight( 0, 1.0 ) ]
   fit = AgeRecencyFit( 19, mix, 12 )

   assert fit.row() == AgeRecencyWeights( 19, mix )
