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
   landing = {
      'seasonTotals': [
         _row( season_id, first_games, first, first_toi ),
         _row( season_id, second_games, second, second_toi ),
      ]
   }

   clubs = ClubIceParser.parse( landing, season_id )

   assert clubs == [
      ClubIce( first, first_games, Time.clock( first_toi ) ),
      ClubIce( second, second_games, Time.clock( second_toi ) ),
   ]


def Test_Parse_TestPlayoffRow_ExpectEmpty() -> None:
   season_id = 20252026
   games_played = 7
   team = list( Team )[ Position.FIRST ]
   toi = '12:00'
   playoff_type = NhlClient.REGULAR_SEASON_GAME_TYPE_ID + 1
   landing = {
      'seasonTotals': [
         _row( season_id, games_played, team, toi, game_type_id=playoff_type ),
      ]
   }

   clubs = ClubIceParser.parse( landing, season_id )

   assert clubs == []


def Test_Parse_TestOtherLeague_ExpectEmpty() -> None:
   season_id = 20252026
   games_played = 46
   team = list( Team )[ Position.FIRST ]
   toi = '18:00'
   league = list( ClubLeague )[ Position.FIRST ].value
   landing = {
      'seasonTotals': [
         _row( season_id, games_played, team, toi, league=league ),
      ]
   }

   clubs = ClubIceParser.parse( landing, season_id )

   assert clubs == []


def Test_Parse_TestOtherSeason_ExpectEmpty() -> None:
   season_id = 20252026
   other_season_id = 20242025
   games_played = 82
   team = list( Team )[ Position.FIRST ]
   toi = '20:00'
   landing = {
      'seasonTotals': [
         _row( other_season_id, games_played, team, toi ),
      ]
   }

   clubs = ClubIceParser.parse( landing, season_id )

   assert clubs == []


def Test_SeasonIds_TestTwoSeasons_ExpectNewestFirst() -> None:
   team = list( Team )[ Position.FIRST ]
   recent = 20252026
   older = 20242025
   recent_games = 2
   older_games = 50
   other_league_games = 46
   recent_toi = '21:17'
   older_toi = '16:00'
   other_league_toi = '18:00'
   league = list( ClubLeague )[ Position.FIRST ].value
   landing = {
      'seasonTotals': [
         _row( older, older_games, team, older_toi ),
         _row( recent, recent_games, team, recent_toi ),
         _row( recent, other_league_games, team, other_league_toi, league=league ),
      ]
   }

   season_ids = ClubIceParser.season_ids( landing )

   assert season_ids == [ recent, older ]
