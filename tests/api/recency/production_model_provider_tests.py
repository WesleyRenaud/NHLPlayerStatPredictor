from __future__ import annotations

from pathlib import Path

import pytest

from api.paths import Paths
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.production_model_provider import ProductionModelProvider
from api.recency.production_model_recorder import ProductionModelRecorder


def Test_Read_TestModel_ExpectFileUnchanged(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   ProductionModelRecorder.write( PaceRegressionModel( [] ) )
   contents = { path: path.read_text() for path in ProductionModelProvider.paths() }

   model = ProductionModelProvider.read()

   assert model == PaceRegressionModel( [] )
   assert { path: path.read_text() for path in ProductionModelProvider.paths() } == contents


def Test_Read_TestMissingFile_ExpectExplicitFailure(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   ProductionModelRecorder.write( PaceRegressionModel( [] ) )
   ( tmp_path / 'shots_weights.json' ).unlink()

   with pytest.raises( FileNotFoundError ):
      ProductionModelProvider.read()
