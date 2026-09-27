from __future__ import annotations

import pytest

from api.projections.season_pace import SeasonPace
from api.recency.playoff_pace_adjuster import PlayoffPaceAdjuster


def Test_Adjust_TestSurplus_ExpectWeightedSurplusAdded() -> None:
   pace = SeasonPace( 20.0, 30.0 )
   surplus = SeasonPace( 4.0, 6.0 )
   goal_weight = 0.8
   assist_weight = 0.5

   adjusted = PlayoffPaceAdjuster.adjust( pace, surplus, goal_weight, assist_weight )

   assert adjusted.goals == pytest.approx( pace.goals + goal_weight * surplus.goals )
   assert adjusted.assists == pytest.approx( pace.assists + assist_weight * surplus.assists )


def Test_Adjust_TestNoSurplus_ExpectUnchanged() -> None:
   pace = SeasonPace( 20.0, 30.0 )

   adjusted = PlayoffPaceAdjuster.adjust( pace, SeasonPace.zero(), 0.8, 0.5 )

   assert adjusted == pace
