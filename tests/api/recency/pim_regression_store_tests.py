from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.paths import Paths
from api.recency.pim_regression import PimRegression
from api.recency.pim_regression_model import PimRegressionModel
from api.recency.pim_regression_store import PimRegressionStore


def Test_Write_TestModel_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   model = PimRegressionModel(
      [ PimRegression( constant=3.5, weights=[ 0.7, 0.2 ] ) ],
      nhl_gap_scale=0.85 )

   PimRegressionStore.write( model )

   assert PimRegressionStore.read() == model
   assert PimRegressionStore.path().read_text() == json.dumps( model.to_dict(), indent=2 )