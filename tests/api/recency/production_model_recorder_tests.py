from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.paths import Paths
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pim_multiplier_store import PimMultiplierStore
from api.recency.pim_weight_store import PimWeightStore
from api.recency.production_coefficient import ProductionCoefficient
from api.recency.production_growth import ProductionGrowth
from api.recency.production_list_store import ProductionListStore
from api.recency.production_model_provider import ProductionModelProvider
from api.recency.production_model_recorder import ProductionModelRecorder
from api.recency.production_trajectory_store import ProductionTrajectoryStore
from api.recency.production_weight import ProductionWeight
from api.recency.scoring_component_share_store import ScoringComponentShareStore
from api.recency.scoring_multiplier_store import ScoringMultiplierStore
from api.recency.scoring_weight_store import ScoringWeightStore
from api.recency.shots_multiplier_store import ShotsMultiplierStore
from api.recency.shots_weight_store import ShotsWeightStore


_STORES: list[ type[ ProductionListStore ] ] = [
   ScoringWeightStore,
   ScoringMultiplierStore,
   ProductionTrajectoryStore,
   PimWeightStore,
   PimMultiplierStore,
   ShotsWeightStore,
   ShotsMultiplierStore,
   ScoringComponentShareStore,
]


def _paths( _cls: type[ ProductionModelProvider ] ) -> list[ Path ]:
   return [ store.path() for store in _STORES ]


def Test_Write_TestModel_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   monkeypatch.setattr( ProductionModelProvider, 'paths', classmethod( _paths ) )
   model = PaceRegressionModel( [
      ProductionGrowth( 18, 19, 1.2, 100 )
   ],
      pim_coefficients=[
         ProductionCoefficient( 18, 19, 1.1, 0.7, 100 ),
         ProductionCoefficient( 18, 20, 1.1 * 1.2, 0.4, 80 ),
         ProductionCoefficient( 19, 20, 1.2, 0.6, 90 ),
      ],
      shots_coefficients=[ ProductionCoefficient( 18, 19, 1.3, 0.9, 100 ) ],
      history_weights=[ ProductionWeight( 18, 19, 0.8, 100 ) ] )

   ProductionModelRecorder.write( model )

   assert ProductionModelProvider.read() == model
   assert set( tmp_path.rglob( '*.json' ) ) == set( ProductionModelProvider.paths() )
   for path in ProductionModelProvider.paths():
      assert isinstance( json.loads( path.read_text() ), list )
   multipliers = json.loads( PimMultiplierStore.path().read_text() )
   assert all( item[ 'to_age' ] == item[ 'from_age' ] + 1 for item in multipliers )
   assert all( 'weight' not in item for item in multipliers )
   weights = json.loads( PimWeightStore.path().read_text() )
   assert all( 'multiplier' not in item for item in weights )
