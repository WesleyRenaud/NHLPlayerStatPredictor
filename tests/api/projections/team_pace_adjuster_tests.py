from __future__ import annotations

from api.projections.career_pace import CareerPace
from api.projections.team_pace_adjuster import TeamPaceAdjuster


def Test_Adjust_TestCurrentMinusPrevious_ExpectOnePlusDelta() -> None:
   pace = CareerPace( 30.0, 40.0 )
   current = 0.87
   previous = 1.12
   delta = current - previous
   assert TeamPaceAdjuster.adjust( pace, current, previous ) == CareerPace(
      pace.goals * ( 1.0 + delta ),
      pace.assists * ( 1.0 + delta ) )


def Test_Adjust_TestEqualRates_ExpectUnchanged() -> None:
   pace = CareerPace( 30.0, 40.0 )
   assert TeamPaceAdjuster.adjust( pace, 0.87, 0.87 ) == pace
