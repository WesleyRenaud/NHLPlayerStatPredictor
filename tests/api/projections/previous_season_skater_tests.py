from __future__ import annotations

from api.projections.previous_season_skater import PreviousSeasonSkater
from api.projections.season_pace import SeasonPace
from api.skaters.skater_position import SkaterPosition


def Test_Contribution_TestGames_ExpectGamesTimesPace() -> None:
   pace = SeasonPace( 10.0, 20.0 )
   games = 82
   assert PreviousSeasonSkater( 1, games, pace, SkaterPosition( 'C' ) ).contribution == (
      games * ( pace.goals + pace.assists ) )
