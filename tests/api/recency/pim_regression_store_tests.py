from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.paths import Paths
from api.recency.pim_regression_model import PimRegressionModel
from api.recency.pim_regression_store import PimRegressionStore
from api.recency.production_coefficient import ProductionCoefficient


def Test_Write_TestModel_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   model = PimRegressionModel( [ ProductionCoefficient( 18, 19, 1.2, 0.8, 100 ) ] )

   PimRegressionStore.write( model )

   assert PimRegressionStore.read() == model
   assert PimRegressionStore.path().read_text() == json.dumps( model.to_dict(), indent=2 )


def Test_Read_TestModel_ExpectFileUnchanged(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   content = json.dumps( { 'coefficients': [] } )
   PimRegressionStore.path().write_text( content )

   model = PimRegressionStore.read()

   assert model == PimRegressionModel( [] )
   assert PimRegressionStore.path().read_text() == content
