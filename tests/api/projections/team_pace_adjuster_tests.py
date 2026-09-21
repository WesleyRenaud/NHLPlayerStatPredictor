from __future__ import annotations

from api.projections.career_pace import CareerPace
from api.projections.team_environment import TeamEnvironment
from api.projections.team_pace_adjuster import TeamPaceAdjuster


def Test_Adjust_TestEqualQuality_ExpectUnchanged() -> None:
   pace = CareerPace( 30.0, 40.0 )
   assert TeamPaceAdjuster.adjust( pace, TeamEnvironment( 60.0, 60.0 ) ) == pace


def Test_Adjust_TestBetterRoster_ExpectScaledByRatio() -> None:
   pace = CareerPace( 30.0, 40.0 )
   ratio = 80.0 / 40.0
   assert TeamPaceAdjuster.adjust( pace, TeamEnvironment( 80.0, 40.0 ) ) == CareerPace(
      pace.goals * ratio,
      pace.assists * ratio )


def Test_Adjust_TestZeroLastSeason_ExpectUnchanged() -> None:
   pace = CareerPace( 30.0, 40.0 )
   assert TeamPaceAdjuster.adjust( pace, TeamEnvironment( 80.0, 0.0 ) ) == pace
