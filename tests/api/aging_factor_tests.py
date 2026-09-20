from __future__ import annotations

from api.aging_factor import AgingFactor


def Test_ToDict_TestFactor_ExpectAgeGoalsAssists() -> None:
   factor = AgingFactor( 24, -0.009, 0.002 )
   assert factor.to_dict() == {
      'age': factor.age,
      'goals': factor.goals,
      'assists': factor.assists,
   }


def Test_FromRow_TestDict_ExpectFactor() -> None:
   factor = AgingFactor( 28, -0.07, -0.044 )
   assert AgingFactor.from_row( factor.to_dict() ) == factor
