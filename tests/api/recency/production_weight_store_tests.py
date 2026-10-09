from pathlib import Path

import pytest

from api.paths import Paths
from api.recency.pim_weight_store import PimWeightStore
from api.recency.production_weight import ProductionWeight
from api.recency.production_weight_store import ProductionWeightStore
from api.recency.scoring_weight_store import ScoringWeightStore
from api.recency.shots_weight_store import ShotsWeightStore


@pytest.mark.parametrize( 'store', [ ScoringWeightStore, PimWeightStore, ShotsWeightStore ] )
def Test_Write_TestWeights_ExpectIndependentTypedRoundTrip(
      store: type[ ProductionWeightStore ],
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   weights = [ ProductionWeight( 18, 20, 0.4, 30 ) ]

   store.write( weights )

   assert store.read() == weights
   assert store.path().parent == tmp_path / Paths.WEIGHTS
   assert list( store.path().parent.iterdir() ) == [ store.path() ]
