from __future__ import annotations

from api.projections.career_pace import CareerPace
from api.projections.last_season_group import LastSeasonGroup
from api.projections.last_season_nhl_skater import LastSeasonNhlSkater
from api.projections.last_season_skater import LastSeasonSkater
from api.shared.enums.position import Position
from api.team import Team


def Test_Skaters_TestNhlAndOther_ExpectCombined() -> None:
   nhl = LastSeasonNhlSkater(
      1,
      82.0,
      CareerPace( 10.0, 20.0 ),
      list( Team )[ Position.FIRST ] )
   other = LastSeasonSkater( 2, 46.0, CareerPace( 8.0, 12.0 ) )
   assert LastSeasonGroup( [ nhl ], [ other ] ).skaters() == [ nhl, other ]
