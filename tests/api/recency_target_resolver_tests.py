from __future__ import annotations

from datetime import date

import pytest

import api.recency_target_resolver as recency_target_resolver
from api.recency_target_resolver import RecencyTargetResolver
from api.season import Season
from api.season_length import SeasonLength


def Test_Resolve_TestSeasons_ExpectLastSeasonId(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   seasons = [
      SeasonLength( 20202021, 56, date( 2021, 1, 13 ), date( 2021, 5, 19 ) ),
      SeasonLength( 20212022, 82, date( 2021, 10, 12 ), date( 2022, 4, 29 ) ),
   ]
   monkeypatch.setattr(
      recency_target_resolver.NhlClient,
      'seasons',
      lambda: seasons )

   season_id = RecencyTargetResolver.resolve()

   assert season_id == Season.latest( seasons ).season_id


def Test_Prior_TestSeasons_ExpectSecondLastSeasonId(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   seasons = [
      SeasonLength( 20202021, 56, date( 2021, 1, 13 ), date( 2021, 5, 19 ) ),
      SeasonLength( 20212022, 82, date( 2021, 10, 12 ), date( 2022, 4, 29 ) ),
      SeasonLength( 20222023, 82, date( 2022, 10, 7 ), date( 2023, 4, 13 ) ),
   ]
   monkeypatch.setattr(
      recency_target_resolver.NhlClient,
      'seasons',
      lambda: seasons )

   season_id = RecencyTargetResolver.prior()

   assert season_id == Season.prior( seasons ).season_id
