from __future__ import annotations

from api.depth.club_ice import ClubIce
from api.ingest.club_ice_parser import ClubIceParser
from api.ingest.nhl_client import NhlClient
from api.shared.enums.position import Position
from api.skaters.club_league import ClubLeague
from api.skaters.team import Team
from api.time import Time


def _full_name( team: Team ) -> str:
   return team.name.replace( '_', ' ' ).title()


def _row(
      season_id: int,
      games_played: int,
      team: Team,
      toi: str,
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
      'avgToi': toi,
      'teamName': { 'default': _full_name( team ) },
   }


def Test_Parse_TestSplitSeason_ExpectClubIce() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   season_id = 20252026
   first_games = 50
   second_games = 22
   first_toi = '14:19'
   second_toi = '12:13'
   assert ClubIceParser.parse(
      {
         'seasonTotals': [
            _row( season_id, first_games, first, first_toi ),
            _row( season_id, second_games, second, second_toi ),
         ]
      },
      season_id ) == [
         ClubIce( first, first_games, Time.clock( first_toi ) ),
         ClubIce( second, second_games, Time.clock( second_toi ) ),
      ]


def Test_Parse_TestPlayoffRow_ExpectEmpty() -> None:
   assert ClubIceParser.parse(
      {
         'seasonTotals': [
            _row(
               20252026,
               7,
               list( Team )[ Position.FIRST ],
               '12:00',
               game_type_id=NhlClient.REGULAR_SEASON_GAME_TYPE_ID + 1 ),
         ]
      },
      20252026 ) == []


def Test_Parse_TestOtherLeague_ExpectEmpty() -> None:
   assert ClubIceParser.parse(
      {
         'seasonTotals': [
            _row(
               20252026,
               46,
               list( Team )[ Position.FIRST ],
               '18:00',
               league=list( ClubLeague )[ Position.FIRST ].value ),
         ]
      },
      20252026 ) == []


def Test_Parse_TestOtherSeason_ExpectEmpty() -> None:
   assert ClubIceParser.parse(
      {
         'seasonTotals': [
            _row( 20242025, 82, list( Team )[ Position.FIRST ], '20:00' ),
         ]
      },
      20252026 ) == []


def Test_SeasonIds_TestTwoSeasons_ExpectNewestFirst() -> None:
   team = list( Team )[ Position.FIRST ]
   recent = 20252026
   older = 20242025
   assert ClubIceParser.season_ids(
      {
         'seasonTotals': [
            _row( older, 50, team, '16:00' ),
            _row( recent, 2, team, '21:17' ),
            _row(
               recent,
               46,
               team,
               '18:00',
               league=list( ClubLeague )[ Position.FIRST ].value ),
         ]
      } ) == [ recent, older ]
