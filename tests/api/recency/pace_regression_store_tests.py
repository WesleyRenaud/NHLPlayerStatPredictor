from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.paths import Paths
from api.projections.scoring_stat import ScoringStat
from api.recency.pace_regression import PaceRegression
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pace_regression_store import PaceRegressionStore
from api.recency.prior_source import PriorSource
from api.recency.production_coefficient import ProductionCoefficient


def Test_Write_TestModel_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   model = PaceRegressionModel( [
      PaceRegression( PriorSource.NHL, ScoringStat.EVEN_STRENGTH_GOALS, [ ProductionCoefficient( 18, 19, 1.2, 0.8, 100 ) ] )
   ],
      pim_coefficients=[ ProductionCoefficient( 18, 19, 1.1, 0.7, 100 ) ],
      shots_coefficients=[ ProductionCoefficient( 18, 19, 1.3, 0.9, 100 ) ] )

   PaceRegressionStore.write( model )

   assert PaceRegressionStore.read() == model
   assert PaceRegressionStore.path().read_text() == json.dumps( model.to_dict(), indent=2 )


def Test_Read_TestModel_ExpectFileUnchanged(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   content = json.dumps( PaceRegressionModel( [] ).to_dict() )
   PaceRegressionStore.path().write_text( content )

   model = PaceRegressionStore.read()

   assert model == PaceRegressionModel( [] )
   assert PaceRegressionStore.path().read_text() == content
