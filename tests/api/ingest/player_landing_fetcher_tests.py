from __future__ import annotations

import pytest

import api.ingest.player_landing_fetcher as player_landing_fetcher
from api.ingest.player_landing_fetcher import PlayerLandingFetcher


def Test_Fetch_TestLandings_ExpectPlayerOrder(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   first_id = 7
   second_id = 8
   player_ids = [ first_id, second_id ]
   force = True
   forced: list[ bool ] = []
   monkeypatch.setattr(
      player_landing_fetcher.NhlClient,
      'player_landing',
      lambda requested_id, force=False: (
         forced.append( force ) or { 'playerId': requested_id } ) )

   landings = PlayerLandingFetcher.fetch( player_ids, force=force )

   assert list( landings ) == player_ids
   assert landings[ first_id ][ 'playerId' ] == first_id
   assert landings[ second_id ][ 'playerId' ] == second_id
   assert forced == [ force, force ]


def Test_Fetch_TestFetchError_ExpectSkipped(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   player_id = 1

   def fake_landing( requested_id: int, force: bool = False ) -> dict[ str, object ]:
      raise RuntimeError( 'landing' )

   monkeypatch.setattr(
      player_landing_fetcher.NhlClient,
      'player_landing',
      fake_landing )

   landings = PlayerLandingFetcher.fetch( [ player_id ] )

   assert landings == {}


def Test_Fetch_TestFetchErrorAmongPlayers_ExpectRemaining(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   missing_id = 1
   ok_id = 8
   landing = { 'playerId': ok_id }

   def fake_landing( requested_id: int, force: bool = False ) -> dict[ str, object ]:
      if requested_id == missing_id:
         raise RuntimeError( 'landing' )

      return landing

   monkeypatch.setattr(
      player_landing_fetcher.NhlClient,
      'player_landing',
      fake_landing )

   landings = PlayerLandingFetcher.fetch( [ missing_id, ok_id ] )

   assert list( landings ) == [ ok_id ]
   assert landings[ ok_id ] == landing
