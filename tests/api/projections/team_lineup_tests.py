from __future__ import annotations

from api.projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.projections.team_lineup import TeamLineup
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _skater(
      player_id: int,
      team: Team,
      points: float ) -> CurrentSeasonNhlSkater:
   return CurrentSeasonNhlSkater(
      player_id,
      SeasonPace( points / 2.0, points / 2.0 ),
      team,
      SkaterPosition( 'C' ) )


def Test_Group_TestTeams_ExpectSeparated() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   first = _skater( 1, now, 50.0 )
   second = _skater( 2, previous, 40.0 )
   third = _skater( 3, now, 30.0 )

   lineups = TeamLineup.group( [ first, second, third ] )

   assert lineups == [
      TeamLineup( now, [ first, third ] ),
      TeamLineup( previous, [ second ] ),
   ]


def Test_Group_TestEmpty_ExpectEmpty() -> None:
   skaters: list[ CurrentSeasonNhlSkater ] = []

   lineups = TeamLineup.group( skaters )

   assert lineups == []


def Test_Total_TestRows_ExpectContributionSum() -> None:
   now = list( Team )[ Position.FIRST ]
   first = _skater( 1, now, 50.0 )
   second = _skater( 2, now, 30.0 )
   lineup = TeamLineup( now, [ first, second ] )

   total = lineup.total()

   assert total == first.contribution + second.contribution
