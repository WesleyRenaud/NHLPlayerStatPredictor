from __future__ import annotations

from datetime import date

import pytest

from api.other_league_season import OtherLeagueSeason
import api.other_league_season_ingester as other_league_season_ingester
from api.other_league_season_ingester import OtherLeagueSeasonIngester
from api.season_length import SeasonLength


def Test_BuildRows_TestLanding_ExpectBuilderRows(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   player_id = 7
   landing = { 'playerId': player_id }
   seasons = [
      SeasonLength( 20252026, 82, date( 2025, 10, 8 ), date( 2026, 4, 17 ) ) ]
   pace_games = 84
   expected = [
      OtherLeagueSeason(
         player_id=player_id,
         season_id=20252026,
         league='AAA',
         age=20.8,
         games_played=46,
         goals=6,
         assists=13,
         points=19,
         g_pace=10.0,
         a_pace=20.0 ) ]
   captured: list[ tuple[ dict[ str, object ], list[ SeasonLength ], int ] ] = []
   monkeypatch.setattr(
      other_league_season_ingester.NhlClient,
      'player_landing',
      lambda requested_id, force=False: landing )
   monkeypatch.setattr(
      other_league_season_ingester.OtherLeagueSeasonBuilder,
      'build',
      lambda payload, season_rows, pace: captured.append(
         ( payload, season_rows, pace ) ) or expected )
   rows = OtherLeagueSeasonIngester.build_rows(
      [ player_id ], seasons, pace_games )
   assert rows == expected
   assert captured == [ ( landing, seasons, pace_games ) ]


def Test_BuildRows_TestFetchError_ExpectSkipped(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   def fake_landing( requested_id: int, force: bool = False ) -> dict[ str, object ]:
      raise RuntimeError( 'landing' )

   monkeypatch.setattr(
      other_league_season_ingester.NhlClient,
      'player_landing',
      fake_landing )
   rows = OtherLeagueSeasonIngester.build_rows( [ 1 ], [], 84 )
   assert rows == []
