from __future__ import annotations

from datetime import date

import pytest

import api.ingest.season_games as season_games
import api.ingest.skater_games_fetcher as skater_games_fetcher
from api.ingest.skater_games_fetcher import SkaterGamesFetcher
from api.season_length import SeasonLength
from api.skaters.skater_summary import SkaterSummary


def _summary( player_id: int, games: int ) -> SkaterSummary:
   return SkaterSummary.from_row( {
      'playerId': player_id, 'skaterFullName': 'Stub Skater', 'positionCode': 'C', 'teamAbbrevs': 'CHI',
      'gamesPlayed': games, 'goals': 1, 'assists': 1, 'points': 2,
      'penaltyMinutes': 0, 'evGoals': 1, 'evPoints': 2,
      'ppGoals': 0, 'ppPoints': 0, 'shGoals': 0, 'shPoints': 0,
      'shots': 4, 'timeOnIcePerGame': 1200.0,
   } )


def Test_GamesPlayed_TestPlayer_ExpectGames(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   season_id = 20262027
   player_id = 7
   player_games = 2
   monkeypatch.setattr( season_games.NhlClient, 'seasons', lambda: [
      SeasonLength( season_id, 84, date( 2026, 10, 7 ), date( 2027, 4, 16 ) ),
   ] )
   monkeypatch.setattr( skater_games_fetcher.NhlClient, 'skater_summary', lambda requested_id: [
      _summary( 8, 4 ),
      _summary( player_id, player_games ),
   ] )

   games = SkaterGamesFetcher.games_played( season_id, player_id, date( 2026, 10, 13 ) )

   assert games == player_games


def Test_GamesPlayed_TestNoRow_ExpectZero(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   season_id = 20262027
   monkeypatch.setattr( season_games.NhlClient, 'seasons', lambda: [
      SeasonLength( season_id, 84, date( 2026, 10, 7 ), date( 2027, 4, 16 ) ),
   ] )
   monkeypatch.setattr( skater_games_fetcher.NhlClient, 'skater_summary', lambda requested_id: [
      _summary( 8, 4 ),
   ] )

   games = SkaterGamesFetcher.games_played( season_id, 7, date( 2026, 10, 13 ) )

   assert games == 0
