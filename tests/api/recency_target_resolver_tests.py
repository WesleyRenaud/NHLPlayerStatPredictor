from __future__ import annotations

from datetime import date

import pytest

import api.recency_target_resolver as recency_target_resolver
from api.recency_target_resolver import RecencyTargetResolver
from api.season_length import SeasonLength
from api.shared.enums.position import Position


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
   assert RecencyTargetResolver.resolve() == sorted( seasons )[ Position.LAST ].season_id
