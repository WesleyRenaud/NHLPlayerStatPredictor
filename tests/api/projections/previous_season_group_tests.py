from __future__ import annotations

from api.projections.previous_season_group import PreviousSeasonGroup
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.previous_season_skater import PreviousSeasonSkater
from api.projections.season_pace import SeasonPace
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_Skaters_TestNhlAndOther_ExpectCombined() -> None:
   nhl = PreviousSeasonNhlSkater(
      1,
      82,
      SeasonPace( 10.0, 20.0 ),
      SkaterPosition( 'C' ),
      list( Team )[ Position.FIRST ] )
   other = PreviousSeasonSkater( 2, 46, SeasonPace( 8.0, 12.0 ), SkaterPosition( 'C' ) )
   assert PreviousSeasonGroup( [ nhl ], [ other ] ).skaters() == [ nhl, other ]
