from __future__ import annotations

from datetime import date

from api.club_league import ClubLeague
from api.nhl_client import NhlClient
from api.other_league_season_builder import OtherLeagueSeasonBuilder
from api.season import Season
from api.season_length import SeasonLength
from api.shared.enums.position import Position


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
      'birthDate': '2005-01-09',
      'seasonTotals': totals,
   }


def Test_Build_TestClubSeason_ExpectPacedRow() -> None:
   league = _league()
   season_id = 20252026
   games_played = 46
   goals = 6
   assists = 13
   pace_games = 84
   start_date = date( 2025, 10, 8 )
   rows = OtherLeagueSeasonBuilder.build(
      _landing( 1, league, season_id, games_played, goals, assists ),
      [ SeasonLength( season_id, 82, start_date, date( 2026, 4, 17 ) ) ],
      pace_games )
   assert len( rows ) == 1
   row = rows[ Position.FIRST ]
   assert row.player_id == 1
   assert row.season_id == season_id
   assert row.league == league
   assert row.games_played == games_played
   assert row.goals == goals
   assert row.assists == assists
   assert row.g_pace == Season.pace( float( goals ), float( games_played ), pace_games )
   assert row.a_pace == Season.pace( float( assists ), float( games_played ), pace_games )
   assert row.age == Season.age_on( date( 2005, 1, 9 ), start_date )


def Test_Build_TestUnknownLeague_ExpectEmpty() -> None:
   rows = OtherLeagueSeasonBuilder.build(
      _landing( 1, _league() + '_', 20252026, 46, 6, 13 ),
      [],
      84 )
   assert rows == []


def Test_Build_TestPlayoffs_ExpectEmpty() -> None:
   rows = OtherLeagueSeasonBuilder.build(
      _landing(
         1,
         _league(),
         20252026,
         46,
         6,
         13,
         game_type_id=NhlClient.REGULAR_SEASON_GAME_TYPE_ID + 1 ),
      [],
      84 )
   assert rows == []


def Test_Build_TestZeroGames_ExpectEmpty() -> None:
   rows = OtherLeagueSeasonBuilder.build(
      _landing( 1, _league(), 20252026, 0, 6, 13 ),
      [],
      84 )
   assert rows == []


def Test_Build_TestSplitSeason_ExpectSummed() -> None:
   league = _league()
   season_id = 20252026
   start_date = date( 2025, 10, 8 )
   rows = OtherLeagueSeasonBuilder.build(
      _landing(
         1,
         league,
         season_id,
         20,
         2,
         4,
         extra_totals=[
            {
               'leagueAbbrev': league,
               'season': season_id,
               'gameTypeId': NhlClient.REGULAR_SEASON_GAME_TYPE_ID,
               'gamesPlayed': 26,
               'goals': 4,
               'assists': 9,
               'points': 13,
            }
         ] ),
      [ SeasonLength( season_id, 82, start_date, date( 2026, 4, 17 ) ) ],
      84 )
   assert len( rows ) == 1
   assert rows[ Position.FIRST ].games_played == 46
   assert rows[ Position.FIRST ].goals == 6
   assert rows[ Position.FIRST ].assists == 13
