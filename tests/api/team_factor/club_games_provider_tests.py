from __future__ import annotations

from pathlib import Path

import pytest

from api.ingest.json_file_cache import JsonFileCache
from api.ingest.nhl_client import NhlClient
from api.shared.enums.position import Position
from api.skaters.team import Team
from api.team_factor.club_games import ClubGames
import api.team_factor.club_games_provider as club_games_provider
from api.team_factor.club_games_provider import ClubGamesProvider


def _full_name( team: Team ) -> str:
   return team.name.replace( '_', ' ' ).title()


def Test_Resolve_TestMissingLanding_ExpectEmpty(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      club_games_provider,
      'JsonFileCache',
      lambda: JsonFileCache( tmp_path ) )
   assert ClubGamesProvider.resolve( 1, 20252026 ) == []


def Test_Resolve_TestLanding_ExpectClubGames(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   season_id = 20252026
   first_games = 50
   second_games = 22
   monkeypatch.setattr(
      club_games_provider,
      'JsonFileCache',
      lambda: JsonFileCache( tmp_path ) )
   JsonFileCache( tmp_path ).write_object(
      'player_landing_1',
      {
         'seasonTotals': [
            {
               'leagueAbbrev': 'NHL',
               'season': season_id,
               'gameTypeId': NhlClient.REGULAR_SEASON_GAME_TYPE_ID,
               'gamesPlayed': first_games,
               'teamName': { 'default': _full_name( first ) },
            },
            {
               'leagueAbbrev': 'NHL',
               'season': season_id,
               'gameTypeId': NhlClient.REGULAR_SEASON_GAME_TYPE_ID,
               'gamesPlayed': second_games,
               'teamName': { 'default': _full_name( second ) },
            },
         ]
      } )
   assert ClubGamesProvider.resolve( 1, season_id ) == [
      ClubGames( first, first_games ),
      ClubGames( second, second_games ),
   ]
