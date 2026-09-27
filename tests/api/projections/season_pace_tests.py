from __future__ import annotations

from api.projections.season_pace import SeasonPace


def Test_Zero_TestCall_ExpectNoGoalsOrAssists() -> None:
   pace = SeasonPace.zero()

   assert pace.goals == 0.0
   assert pace.assists == 0.0
