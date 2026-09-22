from __future__ import annotations

from api.projections.previous_season_group import PreviousSeasonGroup
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.previous_season_skater import PreviousSeasonSkater
from api.projections.season_pace import SeasonPace
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


def _other( player_id: int, points: float, games: int = 82 ) -> PreviousSeasonSkater:
   return PreviousSeasonSkater(
      player_id=player_id,
      games=games,
      pace=SeasonPace( points / 2.0, points / 2.0 ),
      position=list( SkaterPosition )[ Position.FIRST ] )


def _nhl(
      player_id: int,
      team: Team,
      points: float,
      games: int = 82 ) -> PreviousSeasonNhlSkater:
   return PreviousSeasonNhlSkater(
      player_id=player_id,
      games=games,
      pace=SeasonPace( points / 2.0, points / 2.0 ),
      team=team,
      position=list( SkaterPosition )[ Position.FIRST ] )


def Test_Resolve_TestCurrentRosterMates_ExpectPreviousSeasonPaceFromAnyClub() -> None:
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
   previous_season = PreviousSeasonGroup(
      [
         _nhl( player_id, previous, 50.0 ),
         incoming_row,
         departed_row,
      ],
      [] )
   environment = TeamEnvironmentResolver.resolve( player_id, roster, previous_season )
   assert environment == TeamEnvironment(
      current_roster_quality=TeamQualityCalculator.average( [ incoming_row ] ),
      previous_roster_quality=TeamQualityCalculator.average( [ departed_row ] ) )


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
   previous_season = PreviousSeasonGroup(
      [ mate_row, outsider_row ],
      [ _other( player_id, 40.0 ) ] )
   environment = TeamEnvironmentResolver.resolve( player_id, roster, previous_season )
   assert environment == TeamEnvironment(
      current_roster_quality=TeamQualityCalculator.average( [ mate_row ] ),
      previous_roster_quality=TeamQualityCalculator.average( [ mate_row, outsider_row ] ) )
