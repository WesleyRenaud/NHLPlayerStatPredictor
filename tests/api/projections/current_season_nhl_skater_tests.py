from __future__ import annotations

from api.projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_Contribution_TestPace_ExpectGoalsPlusAssists() -> None:
   pace = SeasonPace( 10.0, 20.0 )
   skater = CurrentSeasonNhlSkater(
      7,
      pace,
      list( Team )[ Position.FIRST ],
      SkaterPosition( 'C' ) )

   contribution = skater.contribution

   assert contribution == pace.goals + pace.assists
