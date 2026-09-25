from __future__ import annotations

from api.ingest.nhl_client import NhlClient
from api.ingest.nhl_team_split_builder import NhlTeamSplitBuilder
from api.projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from api.projections.season_pace import SeasonPace
from api.season import Season
from api.shared.enums.position import Position
from api.skaters.club_league import ClubLeague
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


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
   player_id = 8482259
   team = _team()
   season_id = 20252026
   games_played = 60
   goals = 19
   assists = 13
   pace_games = 84
   landings = {
      player_id: _landing( player_id, season_id, games_played, goals, assists, team )
   }

   rows = NhlTeamSplitBuilder.build( landings, season_id, pace_games )

   assert rows == [
      PreviousSeasonNhlSkater(
         player_id,
         games_played,
         SeasonPace(
            Season.pace( float( goals ), float( games_played ), pace_games ),
            Season.pace( float( assists ), float( games_played ), pace_games ) ),
         SkaterPosition( 'C' ),
         team )
   ]


def Test_Build_TestSplitSeason_ExpectOneRowPerClub() -> None:
   player_id = 1
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   season_id = 20252026
   pace_games = 84
   first_games = 60
   first_goals = 19
   first_assists = 13
   second_games = 18
   second_goals = 10
   second_assists = 4
   landings = {
      player_id: _landing(
         player_id,
         season_id,
         first_games,
         first_goals,
         first_assists,
         first,
         extra_totals=[
            {
               'leagueAbbrev': 'NHL',
               'season': season_id,
               'gameTypeId': NhlClient.REGULAR_SEASON_GAME_TYPE_ID,
               'gamesPlayed': second_games,
               'goals': second_goals,
               'assists': second_assists,
               'points': second_goals + second_assists,
               'teamName': { 'default': _full_name( second ) },
            }
         ] )
   }

   rows = NhlTeamSplitBuilder.build( landings, season_id, pace_games )

   assert [ ( row.team, row.games, row.pace.goals, row.pace.assists ) for row in rows ] == [
      (
         first,
         first_games,
         Season.pace( float( first_goals ), float( first_games ), pace_games ),
         Season.pace( float( first_assists ), float( first_games ), pace_games ) ),
      (
         second,
         second_games,
         Season.pace( float( second_goals ), float( second_games ), pace_games ),
         Season.pace( float( second_assists ), float( second_games ), pace_games ) ),
   ]


def Test_Build_TestAccentedClubName_ExpectTeam() -> None:
   player_id = 1
   season_id = 20252026
   pace_games = 84
   club_name = 'Montréal Canadiens'
   team = Team( 'MTL' )
   landings = {
      player_id: {
         'playerId': player_id,
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
               'teamName': { 'default': club_name },
            }
         ],
      }
   }

   rows = NhlTeamSplitBuilder.build( landings, season_id, pace_games )

   assert [ row.team for row in rows ] == [ team ]


def Test_Build_TestDottedClubName_ExpectTeam() -> None:
   player_id = 1
   season_id = 20252026
   pace_games = 84
   club_name = 'St. Louis Blues'
   team = Team( 'STL' )
   landings = {
      player_id: {
         'playerId': player_id,
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
               'teamName': { 'default': club_name },
            }
         ],
      }
   }

   rows = NhlTeamSplitBuilder.build( landings, season_id, pace_games )

   assert [ row.team for row in rows ] == [ team ]


def Test_Build_TestPlayoffRow_ExpectEmpty() -> None:
   player_id = 1
   season_id = 20252026
   pace_games = 84
   playoff_type = NhlClient.REGULAR_SEASON_GAME_TYPE_ID + 1
   landings = {
      player_id: _landing(
         player_id,
         season_id,
         6,
         2,
         2,
         game_type_id=playoff_type )
   }

   rows = NhlTeamSplitBuilder.build( landings, season_id, pace_games )

   assert rows == []


def Test_Build_TestOtherLeague_ExpectEmpty() -> None:
   player_id = 1
   season_id = 20252026
   pace_games = 84
   league = list( ClubLeague )[ Position.FIRST ].value
   landings = {
      player_id: _landing(
         player_id,
         season_id,
         46,
         6,
         13,
         league=league )
   }

   rows = NhlTeamSplitBuilder.build( landings, season_id, pace_games )

   assert rows == []


def Test_Build_TestOtherSeason_ExpectEmpty() -> None:
   player_id = 1
   season_id = 20252026
   other_season_id = 20242025
   pace_games = 84
   landings = { player_id: _landing( player_id, other_season_id, 82, 20, 20 ) }

   rows = NhlTeamSplitBuilder.build( landings, season_id, pace_games )

   assert rows == []


def Test_Build_TestZeroGames_ExpectEmpty() -> None:
   player_id = 1
   season_id = 20252026
   pace_games = 84
   landings = { player_id: _landing( player_id, season_id, 0, 0, 0 ) }

   rows = NhlTeamSplitBuilder.build( landings, season_id, pace_games )

   assert rows == []
