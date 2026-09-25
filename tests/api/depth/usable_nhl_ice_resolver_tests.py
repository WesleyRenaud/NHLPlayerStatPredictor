from __future__ import annotations

from api.depth.club_ice import ClubIce
from api.depth.usable_nhl_ice import UsableNhlIce
from api.depth.usable_nhl_ice_resolver import UsableNhlIceResolver
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


def Test_Resolve_TestStint_ExpectThatSeason() -> None:
   team = list( Team )[ Position.FIRST ]
   season_id = 20252026
   toi = '17:02'
   ice = UsableNhlIceResolver.resolve(
      {
         'seasonTotals': [
            _row(
               season_id,
               UsableNhlIce.MIN_GAMES,
               team,
               toi ),
         ]
      } )
   assert ice == UsableNhlIce(
      season_id,
      Time.clock( toi ),
      ClubIceParser.parse(
         { 'seasonTotals': [ _row( season_id, UsableNhlIce.MIN_GAMES, team, toi ) ] },
         season_id ) )


def Test_Resolve_TestShortThenOlder_ExpectOlder() -> None:
   team = list( Team )[ Position.FIRST ]
   recent = 20252026
   older = 20242025
   recent_toi = '21:17'
   older_toi = '16:04'
   ice = UsableNhlIceResolver.resolve(
      {
         'seasonTotals': [
            _row( recent, 2, team, recent_toi ),
            _row( older, 50, team, older_toi ),
         ]
      } )
   assert ice is not None
   assert ice.season_id == older
   assert ice.toi == Time.clock( older_toi )
   assert ice.clubs == [ ClubIce( team, 50, Time.clock( older_toi ) ) ]


def Test_Resolve_TestOnlyShort_ExpectNone() -> None:
   assert UsableNhlIceResolver.resolve(
      {
         'seasonTotals': [
            _row( 20252026, 2, list( Team )[ Position.FIRST ], '21:17' ),
         ]
      } ) is None


def Test_Resolve_TestOtherLeague_ExpectNone() -> None:
   assert UsableNhlIceResolver.resolve(
      {
         'seasonTotals': [
            _row(
               20252026,
               46,
               list( Team )[ Position.FIRST ],
               '18:00',
               league=list( ClubLeague )[ Position.FIRST ].value ),
         ]
      } ) is None


def Test_Resolve_TestSplitSeason_ExpectWeightedToi() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   season_id = 20252026
   first_games = 50
   second_games = 22
   first_toi = '14:19'
   second_toi = '12:13'
   landing = {
      'seasonTotals': [
         _row( season_id, first_games, first, first_toi ),
         _row( season_id, second_games, second, second_toi ),
      ]
   }
   ice = UsableNhlIceResolver.resolve( landing )
   clubs = ClubIceParser.parse( landing, season_id )
   games = first_games + second_games
   assert ice == UsableNhlIce(
      season_id,
      (
         Time.clock( first_toi ) * first_games
         + Time.clock( second_toi ) * second_games
      ) / games,
      clubs )


def Test_Resolve_TestEmpty_ExpectNone() -> None:
   assert UsableNhlIceResolver.resolve( {} ) is None
