from __future__ import annotations

from api.aging.aging_factor import AgingFactor


def Test_ToDict_TestFactor_ExpectAgeGoalsAssists() -> None:
   factor = AgingFactor( 24, -0.009, 0.002 )

   payload = factor.to_dict()

   assert payload == {
      'age': factor.age,
      'goals': factor.goals,
      'assists': factor.assists,
   }


def Test_FromRow_TestDict_ExpectFactor() -> None:
   factor = AgingFactor( 28, -0.07, -0.044 )

   loaded = AgingFactor.from_row( factor.to_dict() )

   assert loaded == factor
