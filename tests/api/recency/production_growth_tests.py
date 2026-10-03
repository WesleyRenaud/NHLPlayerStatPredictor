from __future__ import annotations

from api.recency.production_growth import ProductionGrowth


def Test_FromRow_TestAgePairs_ExpectRoundTrip() -> None:
   growth = ProductionGrowth( 18, 19, 1.2, 100 )

   assert ProductionGrowth.from_row( growth.to_dict() ) == growth
   assert 'weight' not in growth.to_dict()
