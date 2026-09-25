from __future__ import annotations

from api.projections.season_pace import SeasonPace
from api.projections.team_pace_adjuster import TeamPaceAdjuster


def Test_Adjust_TestCurrentMinusPrevious_ExpectOnePlusDelta() -> None:
   pace = SeasonPace( 30.0, 40.0 )
   current = 0.87
   previous = 1.12
   delta = current - previous

   adjusted = TeamPaceAdjuster.adjust( pace, current, previous )

   assert adjusted == SeasonPace(
      pace.goals * ( 1.0 + delta ),
      pace.assists * ( 1.0 + delta ) )


def Test_Adjust_TestEqualRates_ExpectUnchanged() -> None:
   pace = SeasonPace( 30.0, 40.0 )
   rate = 0.87

   adjusted = TeamPaceAdjuster.adjust( pace, rate, rate )

   assert adjusted == pace
