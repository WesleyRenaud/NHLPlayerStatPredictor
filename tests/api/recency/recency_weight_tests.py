from __future__ import annotations

from api.recency.recency_weight import RecencyWeight


def Test_ToDict_TestWeight_ExpectLagAndWeight() -> None:
   weight = RecencyWeight( 2, 0.25 )

   payload = weight.to_dict()

   assert payload == {
      'lag': weight.lag,
      'weight': weight.weight,
   }


def Test_FromRow_TestDict_ExpectWeight() -> None:
   weight = RecencyWeight( 1, 0.5 )

   loaded = RecencyWeight.from_row( weight.to_dict() )

   assert loaded == weight
