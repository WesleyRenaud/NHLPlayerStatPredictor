from __future__ import annotations

from datetime import date
from unittest.mock import Mock

import pytest

import api.ingest.season_games as season_games
from api.ingest.season_games import SeasonGames
from api.season_length import SeasonLength


def _seasons( season_id: int ) -> list[ SeasonLength ]:
   return [ SeasonLength( season_id, 84, date( 2026, 10, 7 ), date( 2027, 4, 16 ) ) ]


def Test_Played_TestBeforeSeason_ExpectZero(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   season_id = 20262027
   games = Mock( return_value=6 )
   monkeypatch.setattr( season_games.NhlClient, 'seasons', lambda: _seasons( season_id ) )

   played = SeasonGames.played( season_id, date( 2026, 10, 6 ), games )

   assert played == 0
   games.assert_not_called()


def Test_Played_TestStartedSeason_ExpectGames(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   season_id = 20262027
   team_games = 6
   games = Mock( return_value=team_games )
   monkeypatch.setattr( season_games.NhlClient, 'seasons', lambda: _seasons( season_id ) )

   played = SeasonGames.played( season_id, date( 2026, 10, 13 ), games )

   assert played == team_games
   games.assert_called_once_with()
