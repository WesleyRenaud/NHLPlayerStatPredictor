from __future__ import annotations

from dataclasses import fields

from api.projections.power_play_pace import PowerPlayPace
from api.projections.scoring_paces import ScoringPaces
from api.projections.scoring_stat import ScoringStat
from api.projections.season_pace import SeasonPace
from api.projections.short_handed_pace import ShortHandedPace


def Test_Paces_TestComponents_ExpectUnalteredValues() -> None:
   pace = ScoringPaces( 2.0, 3.0, 3.0, 6.0, 1.0, 2.0 )

   assert pace.season_pace() == SeasonPace( pace.goals, pace.assists )
   assert pace.power_play_pace() == PowerPlayPace( pace.power_play_goals, pace.power_play_assists )
   assert pace.short_handed_pace() == ShortHandedPace( pace.short_handed_goals, pace.short_handed_assists )


def Test_Paces_TestScoringStats_ExpectEnumMatchesFields() -> None:
   assert { stat.value for stat in ScoringStat } == { field.name for field in fields( ScoringPaces ) }
