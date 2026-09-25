from __future__ import annotations

from pathlib import Path

import pytest

from api.depth.club_ice import ClubIce
import api.depth.club_ice_provider as club_ice_provider
from api.depth.club_ice_provider import ClubIceProvider
from api.depth.usable_nhl_ice import UsableNhlIce
from api.depth.usable_nhl_ice_resolver import UsableNhlIceResolver
from api.ingest.json_file_cache import JsonFileCache
from api.ingest.nhl_client import NhlClient
from api.shared.enums.position import Position
from api.skaters.team import Team
from api.time import Time


def _full_name( team: Team ) -> str:
   return team.name.replace( '_', ' ' ).title()


def Test_Resolve_TestMissingLanding_ExpectNone(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      club_ice_provider,
      'JsonFileCache',
      lambda: JsonFileCache( tmp_path ) )
   assert ClubIceProvider.resolve( 1 ) is None


def Test_Resolve_TestLanding_ExpectIce(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   team = list( Team )[ Position.FIRST ]
   season_id = 20252026
   toi = '17:02'
   games = UsableNhlIceResolver.MIN_GAMES
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
               'gamesPlayed': games,
               'avgToi': toi,
               'teamName': { 'default': _full_name( team ) },
            },
         ]
      } )
   assert ClubIceProvider.resolve( 1 ) == UsableNhlIce(
      season_id,
      Time.clock( toi ),
      [ ClubIce( team, games, Time.clock( toi ) ) ] )
