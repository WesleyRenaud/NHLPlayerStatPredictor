from __future__ import annotations

import pytest

import api.ingest.player_landing_fetcher as player_landing_fetcher
from api.ingest.player_landing_fetcher import PlayerLandingFetcher


def Test_Fetch_TestLandings_ExpectPlayerOrder(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   first_id = 7
   second_id = 8
   forced: list[ bool ] = []
   monkeypatch.setattr(
      player_landing_fetcher.NhlClient,
      'player_landing',
      lambda requested_id, force=False: (
         forced.append( force ) or { 'playerId': requested_id } ) )
   landings = PlayerLandingFetcher.fetch( [ first_id, second_id ], force=True )
   assert list( landings ) == [ first_id, second_id ]
   assert landings[ first_id ][ 'playerId' ] == first_id
   assert landings[ second_id ][ 'playerId' ] == second_id
   assert forced == [ True, True ]


def Test_Fetch_TestFetchError_ExpectSkipped(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   def fake_landing( requested_id: int, force: bool = False ) -> dict[ str, object ]:
      raise RuntimeError( 'landing' )

   monkeypatch.setattr(
      player_landing_fetcher.NhlClient,
      'player_landing',
      fake_landing )
   assert PlayerLandingFetcher.fetch( [ 1 ] ) == {}


def Test_Fetch_TestFetchErrorAmongPlayers_ExpectRemaining(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   ok_id = 8
   landing = { 'playerId': ok_id }

   def fake_landing( requested_id: int, force: bool = False ) -> dict[ str, object ]:
      if requested_id == 1:
         raise RuntimeError( 'landing' )

      return landing

   monkeypatch.setattr(
      player_landing_fetcher.NhlClient,
      'player_landing',
      fake_landing )
   landings = PlayerLandingFetcher.fetch( [ 1, ok_id ] )
   assert list( landings ) == [ ok_id ]
   assert landings[ ok_id ] == landing
