from __future__ import annotations

from api.ingest.club_games_parser import ClubGamesParser
from api.ingest.nhl_client import NhlClient
from api.shared.enums.position import Position
from api.skaters.club_league import ClubLeague
from api.skaters.team import Team
from api.team_factor.club_games import ClubGames


def _full_name( team: Team ) -> str:
   return team.name.replace( '_', ' ' ).title()


def _row(
      season_id: int,
      games_played: int,
      team: Team,
      game_type_id: int | None = None,
      league: str = 'NHL' ) -> dict[ str, object ]:
   return {
      'leagueAbbrev': league,
      'season': season_id,
      'gameTypeId': (
         NhlClient.REGULAR_SEASON_GAME_TYPE_ID
         if game_type_id is None
         else game_type_id ),
      'gamesPlayed': games_played,
      'teamName': { 'default': _full_name( team ) },
   }


def Test_Parse_TestSplitSeason_ExpectClubGames() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   season_id = 20252026
   first_games = 50
   second_games = 22
   assert ClubGamesParser.parse(
      {
         'seasonTotals': [
            _row( season_id, first_games, first ),
            _row( season_id, second_games, second ),
         ]
      },
      season_id ) == [
         ClubGames( first, first_games ),
         ClubGames( second, second_games ),
      ]


def Test_Parse_TestPlayoffRow_ExpectEmpty() -> None:
   assert ClubGamesParser.parse(
      {
         'seasonTotals': [
            _row(
               20252026,
               7,
               list( Team )[ Position.FIRST ],
               game_type_id=NhlClient.REGULAR_SEASON_GAME_TYPE_ID + 1 ),
         ]
      },
      20252026 ) == []


def Test_Parse_TestOtherLeague_ExpectEmpty() -> None:
   assert ClubGamesParser.parse(
      {
         'seasonTotals': [
            _row(
               20252026,
               46,
               list( Team )[ Position.FIRST ],
               league=list( ClubLeague )[ Position.FIRST ].value ),
         ]
      },
      20252026 ) == []


def Test_Parse_TestOtherSeason_ExpectEmpty() -> None:
   assert ClubGamesParser.parse(
      {
         'seasonTotals': [
            _row( 20242025, 82, list( Team )[ Position.FIRST ] ),
         ]
      },
      20252026 ) == []
