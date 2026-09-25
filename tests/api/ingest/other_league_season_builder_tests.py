from __future__ import annotations

from datetime import date

from api.ingest.nhl_client import NhlClient
from api.ingest.other_league_season_builder import OtherLeagueSeasonBuilder
from api.season import Season
from api.season_length import SeasonLength
from api.shared.enums.position import Position
from api.skaters.club_league import ClubLeague
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition


def _league() -> str:
   return list( ClubLeague )[ Position.FIRST ].value


def _landing(
      player_id: int,
      league: str,
      season_id: int,
      games_played: int,
      goals: int,
      assists: int,
      game_type_id: int | None = None,
      extra_totals: list[ dict[ str, object ] ] | None = None ) -> dict[ str, object ]:
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
      }
   ]

   if extra_totals:
      totals.extend( extra_totals )

   return {
      'playerId': player_id,
      'position': SkaterPosition( 'C' ).value,
      'birthDate': '2005-01-09',
      'seasonTotals': totals,
   }


def Test_Build_TestClubSeason_ExpectPacedRow() -> None:
   player_id = 1
   league = _league()
   season_id = 20252026
   games_played = 46
   goals = 6
   assists = 13
   pace_games = 84
   start_date = date( 2025, 10, 8 )
   birth_date = date( 2005, 1, 9 )
   position = SkaterPosition( 'C' )
   landing = _landing( player_id, league, season_id, games_played, goals, assists )
   seasons = [ SeasonLength( season_id, 82, start_date, date( 2026, 4, 17 ) ) ]

   rows = OtherLeagueSeasonBuilder.build( landing, seasons, pace_games )

   assert rows == [
      OtherLeagueSkaterSeason(
         player_id=player_id,
         season_id=season_id,
         league=league,
         position=position,
         age=Season.age_on( birth_date, start_date ),
         games_played=games_played,
         goals=goals,
         assists=assists,
         points=goals + assists,
         g_pace=Season.pace( float( goals ), float( games_played ), pace_games ),
         a_pace=Season.pace( float( assists ), float( games_played ), pace_games ) )
   ]


def Test_Build_TestUnknownLeague_ExpectEmpty() -> None:
   player_id = 1
   league = f'{ _league() }_'
   season_id = 20252026
   pace_games = 84
   landing = _landing( player_id, league, season_id, 46, 6, 13 )

   rows = OtherLeagueSeasonBuilder.build( landing, [], pace_games )

   assert rows == []


def Test_Build_TestPlayoffs_ExpectEmpty() -> None:
   player_id = 1
   league = _league()
   season_id = 20252026
   pace_games = 84
   playoff_type = NhlClient.REGULAR_SEASON_GAME_TYPE_ID + 1
   landing = _landing(
      player_id,
      league,
      season_id,
      46,
      6,
      13,
      game_type_id=playoff_type )

   rows = OtherLeagueSeasonBuilder.build( landing, [], pace_games )

   assert rows == []


def Test_Build_TestMissingGamesPlayed_ExpectEmpty() -> None:
   player_id = 1
   league = _league()
   season_id = 20252026
   pace_games = 84
   landing = _landing( player_id, league, season_id, 46, 6, 13 )
   del landing[ 'seasonTotals' ][ Position.FIRST ][ 'gamesPlayed' ]
   seasons = [ SeasonLength( season_id, 82, date( 2025, 10, 8 ), date( 2026, 4, 17 ) ) ]

   rows = OtherLeagueSeasonBuilder.build( landing, seasons, pace_games )

   assert rows == []


def Test_Build_TestUnknownSeason_ExpectEmpty() -> None:
   player_id = 1
   league = _league()
   season_id = 20252026
   other_season_id = 20242025
   pace_games = 84
   landing = _landing( player_id, league, other_season_id, 46, 6, 13 )
   seasons = [ SeasonLength( season_id, 82, date( 2025, 10, 8 ), date( 2026, 4, 17 ) ) ]

   rows = OtherLeagueSeasonBuilder.build( landing, seasons, pace_games )

   assert rows == []


def Test_Build_TestZeroGames_ExpectEmpty() -> None:
   player_id = 1
   league = _league()
   season_id = 20252026
   pace_games = 84
   landing = _landing( player_id, league, season_id, 0, 6, 13 )

   rows = OtherLeagueSeasonBuilder.build( landing, [], pace_games )

   assert rows == []


def Test_Build_TestSplitSeason_ExpectSummed() -> None:
   player_id = 1
   league = _league()
   season_id = 20252026
   start_date = date( 2025, 10, 8 )
   first_games = 20
   first_goals = 2
   first_assists = 4
   second_games = 26
   second_goals = 4
   second_assists = 9
   pace_games = 84
   landing = _landing(
      player_id,
      league,
      season_id,
      first_games,
      first_goals,
      first_assists,
      extra_totals=[
         {
            'leagueAbbrev': league,
            'season': season_id,
            'gameTypeId': NhlClient.REGULAR_SEASON_GAME_TYPE_ID,
            'gamesPlayed': second_games,
            'goals': second_goals,
            'assists': second_assists,
            'points': second_goals + second_assists,
         }
      ] )
   seasons = [ SeasonLength( season_id, 82, start_date, date( 2026, 4, 17 ) ) ]

   rows = OtherLeagueSeasonBuilder.build( landing, seasons, pace_games )
   row = rows[ Position.FIRST ]

   assert len( rows ) == 1
   assert row.games_played == first_games + second_games
   assert row.goals == first_goals + second_goals
   assert row.assists == first_assists + second_assists
