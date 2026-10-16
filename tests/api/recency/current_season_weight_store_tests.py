from pathlib import Path

import pytest

from api.paths import Paths
from api.recency.current_season_weight import CurrentSeasonWeight
from api.recency.current_season_weight_store import CurrentSeasonWeightStore


def Test_Write_TestWeights_ExpectRoundTrip(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   weights = [ CurrentSeasonWeight( 0.05, 0.25 ), CurrentSeasonWeight( 0.5, 0.6 ) ]

   CurrentSeasonWeightStore.write( weights )

   assert CurrentSeasonWeightStore.read() == weights
   assert CurrentSeasonWeightStore.path().parent == tmp_path / Paths.RECENCY
