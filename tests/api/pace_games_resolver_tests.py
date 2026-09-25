from __future__ import annotations

from datetime import date

import pytest

import api.pace_games_resolver as pace_games_resolver
from api.pace_games_resolver import PaceGamesResolver
from api.season import Season
from api.season_length import SeasonLength


def Test_Resolve_TestSeasons_ExpectPaceGames(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   seasons = [
      SeasonLength( 20202021, 56, date( 2021, 1, 13 ), date( 2021, 5, 19 ) ),
      SeasonLength( 20212022, 82, date( 2021, 10, 12 ), date( 2022, 4, 29 ) ),
   ]
   monkeypatch.setattr(
      pace_games_resolver.NhlClient,
      'seasons',
      lambda: seasons )

   pace_games = PaceGamesResolver.resolve()

   assert pace_games == Season.pace_games( seasons )
