from __future__ import annotations

from api.recency.production_coefficient import ProductionCoefficient


def Test_FromRow_TestCoefficient_ExpectRoundTrip() -> None:
   coefficient = ProductionCoefficient( 18, 19, 1.2, 0.8, 100 )

   assert ProductionCoefficient.from_row( coefficient.to_dict() ) == coefficient
