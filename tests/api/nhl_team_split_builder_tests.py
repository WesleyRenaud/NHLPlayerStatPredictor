from __future__ import annotations

from api.club_league import ClubLeague
from api.nhl_client import NhlClient
from api.nhl_team_split_builder import NhlTeamSplitBuilder
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.season import Season
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _team() -> Team:
   return list( Team )[ Position.FIRST ]


def _full_name( team: Team ) -> str:
   return team.name.replace( '_', ' ' ).title()


def _landing(
      player_id: int,
      season_id: int,
      games_played: int,
      goals: int,
      assists: int,
      team: Team | None = None,
      extra_totals: list[ dict[ str, object ] ] | None = None,
      game_type_id: int | None = None,
      league: str = 'NHL' ) -> dict[ str, object ]:
   club = team if team is not None else _team()
   totals: list[ dict[ str, object ] ] = [
      {
         'leagueAbbrev': league,
         'season': season_id,
         'gameTypeId': (
            NhlClient.REGULAR_SEASON_GAME_TYPE_ID
            if game_type_id is None
            else game_type_id ),
         'gamesPlayed': games_played,
         'goals': goals,
         'assists': assists,
         'points': goals + assists,
         'teamName': { 'default': _full_name( club ) },
      }
   ]

   if extra_totals:
      totals.extend( extra_totals )

   return {
      'playerId': player_id,
      'position': SkaterPosition( 'C' ).value,
      'seasonTotals': totals,
   }


def Test_Build_TestNhlClubSeason_ExpectPacedRow() -> None:
   team = _team()
   season_id = 20252026
   games_played = 60
   goals = 19
   assists = 13
   pace_games = 84
   rows = NhlTeamSplitBuilder.build(
      { 8482259: _landing( 8482259, season_id, games_played, goals, assists, team ) },
      season_id,
      pace_games )
   assert rows == [
      PreviousSeasonNhlSkater(
         8482259,
         games_played,
         SeasonPace(
            Season.pace( float( goals ), float( games_played ), pace_games ),
            Season.pace( float( assists ), float( games_played ), pace_games ) ),
         SkaterPosition( 'C' ),
         team )
   ]


def Test_Build_TestSplitSeason_ExpectOneRowPerClub() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   season_id = 20252026
   pace_games = 84
   rows = NhlTeamSplitBuilder.build(
      {
         1: _landing(
            1,
            season_id,
            60,
            19,
            13,
            first,
            extra_totals=[
               {
                  'leagueAbbrev': 'NHL',
                  'season': season_id,
                  'gameTypeId': NhlClient.REGULAR_SEASON_GAME_TYPE_ID,
                  'gamesPlayed': 18,
                  'goals': 10,
                  'assists': 4,
                  'points': 14,
                  'teamName': { 'default': _full_name( second ) },
               }
            ] )
      },
      season_id,
      pace_games )
   assert [ ( row.team, row.games, row.pace.goals, row.pace.assists ) for row in rows ] == [
      (
         first,
         60,
         Season.pace( 19.0, 60.0, pace_games ),
         Season.pace( 13.0, 60.0, pace_games ) ),
      (
         second,
         18,
         Season.pace( 10.0, 18.0, pace_games ),
         Season.pace( 4.0, 18.0, pace_games ) ),
   ]


def Test_Build_TestAccentedClubName_ExpectTeam() -> None:
   season_id = 20252026
   rows = NhlTeamSplitBuilder.build(
      {
         1: {
            'playerId': 1,
            'position': SkaterPosition( 'C' ).value,
            'seasonTotals': [
               {
                  'leagueAbbrev': 'NHL',
                  'season': season_id,
                  'gameTypeId': NhlClient.REGULAR_SEASON_GAME_TYPE_ID,
                  'gamesPlayed': 82,
                  'goals': 1,
                  'assists': 1,
                  'points': 2,
                  'teamName': { 'default': 'Montréal Canadiens' },
               }
            ],
         }
      },
      season_id,
      84 )
   assert [ row.team for row in rows ] == [ Team( 'MTL' ) ]


def Test_Build_TestDottedClubName_ExpectTeam() -> None:
   season_id = 20252026
   rows = NhlTeamSplitBuilder.build(
      {
         1: {
            'playerId': 1,
            'position': SkaterPosition( 'C' ).value,
            'seasonTotals': [
               {
                  'leagueAbbrev': 'NHL',
                  'season': season_id,
                  'gameTypeId': NhlClient.REGULAR_SEASON_GAME_TYPE_ID,
                  'gamesPlayed': 82,
                  'goals': 1,
                  'assists': 1,
                  'points': 2,
                  'teamName': { 'default': 'St. Louis Blues' },
               }
            ],
         }
      },
      season_id,
      84 )
   assert [ row.team for row in rows ] == [ Team( 'STL' ) ]


def Test_Build_TestPlayoffRow_ExpectEmpty() -> None:
   rows = NhlTeamSplitBuilder.build(
      { 1: _landing( 1, 20252026, 6, 2, 2, game_type_id=3 ) },
      20252026,
      84 )
   assert rows == []


def Test_Build_TestOtherLeague_ExpectEmpty() -> None:
   rows = NhlTeamSplitBuilder.build(
      {
         1: _landing(
            1,
            20252026,
            46,
            6,
            13,
            league=list( ClubLeague )[ Position.FIRST ].value )
      },
      20252026,
      84 )
   assert rows == []


def Test_Build_TestOtherSeason_ExpectEmpty() -> None:
   rows = NhlTeamSplitBuilder.build(
      { 1: _landing( 1, 20242025, 82, 20, 20 ) },
      20252026,
      84 )
   assert rows == []


def Test_Build_TestZeroGames_ExpectEmpty() -> None:
   rows = NhlTeamSplitBuilder.build(
      { 1: _landing( 1, 20252026, 0, 0, 0 ) },
      20252026,
      84 )
   assert rows == []
