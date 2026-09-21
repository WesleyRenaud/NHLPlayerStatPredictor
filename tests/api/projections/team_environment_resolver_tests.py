from __future__ import annotations

from api.projections.career_pace import CareerPace
from api.projections.last_season_group import LastSeasonGroup
from api.projections.last_season_nhl_skater import LastSeasonNhlSkater
from api.projections.last_season_skater import LastSeasonSkater
from api.projections.team_environment import TeamEnvironment
from api.projections.team_environment_resolver import TeamEnvironmentResolver
from api.projections.team_quality_calculator import TeamQualityCalculator
from api.roster_skater import RosterSkater
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _roster( player_id: int, team: Team ) -> RosterSkater:
   return RosterSkater(
      player_id=player_id,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      team=team )


def _other( player_id: int, points: float, games: float = 82.0 ) -> LastSeasonSkater:
   return LastSeasonSkater(
      player_id=player_id,
      games=games,
      pace=CareerPace( points / 2.0, points / 2.0 ) )


def _nhl(
      player_id: int,
      team: Team,
      points: float,
      games: float = 82.0 ) -> LastSeasonNhlSkater:
   return LastSeasonNhlSkater(
      player_id=player_id,
      games=games,
      pace=CareerPace( points / 2.0, points / 2.0 ),
      team=team )


def Test_Resolve_TestNotOnRoster_ExpectAllClubsQuality() -> None:
   team = list( Team )[ Position.FIRST ]
   outsider = _nhl( 2, team, 80.0 )
   last_season = LastSeasonGroup( [ outsider ], [] )
   quality = TeamQualityCalculator.average( [ outsider ] )
   assert TeamEnvironmentResolver.resolve(
      1,
      [ _roster( 2, team ) ],
      last_season ) == TeamEnvironment( quality, quality )


def Test_Resolve_TestCurrentRosterMates_ExpectLastSeasonPaceFromAnyClub() -> None:
   now = list( Team )[ Position.FIRST ]
   previous = list( Team )[ Position.SECOND ]
   elsewhere = list( Team )[ Position.THIRD ]
   player_id = 1
   incoming = 2
   departed = 3
   roster = [
      _roster( player_id, now ),
      _roster( incoming, now ),
   ]
   incoming_row = _nhl( incoming, elsewhere, 100.0 )
   departed_row = _nhl( departed, previous, 20.0 )
   last_season = LastSeasonGroup(
      [
         _nhl( player_id, previous, 50.0 ),
         incoming_row,
         departed_row,
      ],
      [] )
   environment = TeamEnvironmentResolver.resolve( player_id, roster, last_season )
   assert environment == TeamEnvironment(
      roster_quality=TeamQualityCalculator.average( [ incoming_row ] ),
      last_season_quality=TeamQualityCalculator.average( [ departed_row ] ) )


def Test_Resolve_TestMissingLastNhlTeam_ExpectLeagueNhlAverage() -> None:
   now = list( Team )[ Position.FIRST ]
   other = list( Team )[ Position.SECOND ]
   player_id = 1
   mate = 2
   outsider = 3
   roster = [
      _roster( player_id, now ),
      _roster( mate, now ),
   ]
   mate_row = _nhl( mate, other, 80.0 )
   outsider_row = _nhl( outsider, other, 20.0 )
   last_season = LastSeasonGroup(
      [ mate_row, outsider_row ],
      [ _other( player_id, 40.0 ) ] )
   environment = TeamEnvironmentResolver.resolve( player_id, roster, last_season )
   assert environment == TeamEnvironment(
      roster_quality=TeamQualityCalculator.average( [ mate_row ] ),
      last_season_quality=TeamQualityCalculator.average( [ mate_row, outsider_row ] ) )
