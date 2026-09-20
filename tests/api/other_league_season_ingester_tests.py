from __future__ import annotations

from datetime import date

import pytest

import api.other_league_season_ingester as other_league_season_ingester
from api.other_league_season_ingester import OtherLeagueSeasonIngester
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.season_length import SeasonLength


def Test_BuildRows_TestLanding_ExpectBuilderRows(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   player_id = 7
   landing = { 'playerId': player_id }
   seasons = [
      SeasonLength( 20252026, 82, date( 2025, 10, 8 ), date( 2026, 4, 17 ) ) ]
   pace_games = 84
   expected = [
      OtherLeagueSkaterSeason(
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
      other_league_season_ingester.OtherLeagueSeasonBuilder,
      'build',
      lambda payload, season_rows, pace: captured.append(
         ( payload, season_rows, pace ) ) or expected )
   rows = OtherLeagueSeasonIngester.build_rows(
      [ player_id ],
      { player_id: landing },
      seasons,
      pace_games )
   assert rows == expected
   assert captured == [ ( landing, seasons, pace_games ) ]


def Test_BuildRows_TestMissingLanding_ExpectSkipped() -> None:
   rows = OtherLeagueSeasonIngester.build_rows( [ 1 ], {}, [], 84 )
   assert rows == []


def Test_BuildRows_TestMultiplePlayers_ExpectPlayerOrder(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   first_id = 7
   second_id = 8
   seasons = [
      SeasonLength( 20252026, 82, date( 2025, 10, 8 ), date( 2026, 4, 17 ) ) ]
   expected = {
      first_id: OtherLeagueSkaterSeason(
         player_id=first_id,
         season_id=20252026,
         league='AAA',
         age=20.8,
         games_played=46,
         goals=6,
         assists=13,
         points=19,
         g_pace=10.0,
         a_pace=20.0 ),
      second_id: OtherLeagueSkaterSeason(
         player_id=second_id,
         season_id=20252026,
         league='AAA',
         age=20.8,
         games_played=46,
         goals=6,
         assists=13,
         points=19,
         g_pace=10.0,
         a_pace=20.0 ),
   }
   monkeypatch.setattr(
      other_league_season_ingester.OtherLeagueSeasonBuilder,
      'build',
      lambda payload, season_rows, pace: [ expected[ int( payload[ 'playerId' ] ) ] ] )
   rows = OtherLeagueSeasonIngester.build_rows(
      [ first_id, second_id ],
      {
         first_id: { 'playerId': first_id },
         second_id: { 'playerId': second_id },
      },
      seasons,
      84 )
   assert rows == [ expected[ first_id ], expected[ second_id ] ]


def Test_BuildRows_TestMissingLandingAmongPlayers_ExpectRemaining(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   ok_id = 8
   expected = OtherLeagueSkaterSeason(
      player_id=ok_id,
      season_id=20252026,
      league='AAA',
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )
   monkeypatch.setattr(
      other_league_season_ingester.OtherLeagueSeasonBuilder,
      'build',
      lambda payload, season_rows, pace: [ expected ] )
   rows = OtherLeagueSeasonIngester.build_rows(
      [ 1, ok_id ],
      { ok_id: { 'playerId': ok_id } },
      [],
      84 )
   assert rows == [ expected ]
