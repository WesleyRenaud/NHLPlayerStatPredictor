from __future__ import annotations

from api.recency.age_band import AgeBand


def Test_Contains_TestAges_ExpectInclusiveBounds() -> None:
   band = AgeBand( 25, 26 )

   assert not band.contains( 24 )
   assert band.contains( 25 )
   assert band.contains( 26 )
   assert not band.contains( 27 )
