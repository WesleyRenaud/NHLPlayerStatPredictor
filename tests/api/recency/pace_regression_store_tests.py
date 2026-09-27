from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.paths import Paths
from api.recency.age_band import AgeBand
from api.recency.pace_regression import PaceRegression
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pace_regression_store import PaceRegressionStore
from api.recency.prior_source import PriorSource


def Test_Write_TestModel_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   model = PaceRegressionModel(
      [
         PaceRegression( PriorSource.NHL, AgeBand( 18, 22 ), 7.4, [ 0.68 ], 6.1, [ 0.7 ] ),
         PaceRegression( PriorSource.TRANSLATED, AgeBand( 20, 21 ), 4.8, [ 0.6, 0.21 ], 4.2, [ 0.61, 0.2 ] ),
      ],
      0.785,
      0.835 )
   PaceRegressionStore.write( model )

   loaded = PaceRegressionStore.read()
   written = PaceRegressionStore.path().read_text()

   assert loaded == model
   assert written == json.dumps( model.to_dict(), indent=2 )
   assert PaceRegressionStore.path() == tmp_path / PaceRegressionStore.FILE_NAME
