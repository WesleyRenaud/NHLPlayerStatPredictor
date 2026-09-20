from __future__ import annotations

from api.aging_factor import AgingFactor
from api.projections.aging_pace_adjuster import AgingPaceAdjuster
from api.projections.career_pace import CareerPace


def Test_Adjust_TestMatchingAge_ExpectScaledPace() -> None:
   pace = CareerPace( 31.4, 42.1 )
   factor = AgingFactor( 28, -0.07, -0.044 )
   aged = AgingPaceAdjuster.adjust( pace, factor.age, [ factor ] )
   assert aged == CareerPace(
      pace.goals * ( 1.0 + factor.goals ),
      pace.assists * ( 1.0 + factor.assists ) )


def Test_Adjust_TestMissingAge_ExpectNearestFactor() -> None:
   younger = AgingFactor( 24, 0.01, 0.02 )
   older = AgingFactor( 28, -0.07, -0.044 )
   pace = CareerPace( 20.0, 30.0 )
   aged = AgingPaceAdjuster.adjust( pace, 39, [ younger, older ] )
   assert aged == AgingPaceAdjuster.adjust( pace, older.age, [ younger, older ] )
