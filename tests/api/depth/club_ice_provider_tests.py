from __future__ import annotations

from pathlib import Path

import pytest

from api.depth.club_ice import ClubIce
import api.depth.club_ice_provider as club_ice_provider
from api.depth.club_ice_provider import ClubIceProvider
from api.ingest.json_file_cache import JsonFileCache
from api.ingest.nhl_client import NhlClient
from api.shared.enums.position import Position
from api.skaters.team import Team
from api.time import Time


def _full_name( team: Team ) -> str:
   return team.name.replace( '_', ' ' ).title()


def Test_Resolve_TestMissingLanding_ExpectEmpty(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      club_ice_provider,
      'JsonFileCache',
      lambda: JsonFileCache( tmp_path ) )
   assert ClubIceProvider.resolve( 1, 20252026 ) == []


def Test_Resolve_TestLanding_ExpectClubIce(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   season_id = 20252026
   first_games = 50
   second_games = 22
   first_toi = '14:19'
   second_toi = '12:13'
   monkeypatch.setattr(
      club_ice_provider,
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
               'avgToi': first_toi,
               'teamName': { 'default': _full_name( first ) },
            },
            {
               'leagueAbbrev': 'NHL',
               'season': season_id,
               'gameTypeId': NhlClient.REGULAR_SEASON_GAME_TYPE_ID,
               'gamesPlayed': second_games,
               'avgToi': second_toi,
               'teamName': { 'default': _full_name( second ) },
            },
         ]
      } )
   assert ClubIceProvider.resolve( 1, season_id ) == [
      ClubIce( first, first_games, Time.clock( first_toi ) ),
      ClubIce( second, second_games, Time.clock( second_toi ) ),
   ]
