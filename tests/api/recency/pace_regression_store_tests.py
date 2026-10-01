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
         PaceRegression(
            source=PriorSource.NHL,
            band=AgeBand( 18, 22 ),
            goal_constant=7.4,
            goal_weights=[ 0.68 ],
            assist_constant=6.1,
            assist_weights=[ 0.7 ],
            power_play_goal_constant=0.0,
            power_play_goal_weights=[ 0.0 ],
            power_play_assist_constant=0.0,
            power_play_assist_weights=[ 0.0 ],
            short_handed_goal_constant=0.0,
            short_handed_goal_weights=[ 0.0 ],
            short_handed_assist_constant=0.0,
            short_handed_assist_weights=[ 0.0 ] ),
         PaceRegression(
            source=PriorSource.TRANSLATED,
            band=AgeBand( 20, 21 ),
            goal_constant=4.8,
            goal_weights=[ 0.6, 0.21 ],
            assist_constant=4.2,
            assist_weights=[ 0.61, 0.2 ],
            power_play_goal_constant=0.0,
            power_play_goal_weights=[ 0.0, 0.0 ],
            power_play_assist_constant=0.0,
            power_play_assist_weights=[ 0.0, 0.0 ],
            short_handed_goal_constant=0.0,
            short_handed_goal_weights=[ 0.0, 0.0 ],
            short_handed_assist_constant=0.0,
            short_handed_assist_weights=[ 0.0, 0.0 ] ),
      ],
      0.785,
      0.835,
      0.79,
      0.85,
      0.91,
      1.04,
      1.0,
      1.0 )
   PaceRegressionStore.write( model )

   loaded = PaceRegressionStore.read()
   written = PaceRegressionStore.path().read_text()

   assert loaded == model
   assert written == json.dumps( model.to_dict(), indent=2 )
   assert PaceRegressionStore.path() == tmp_path / PaceRegressionStore.FILE_NAME
