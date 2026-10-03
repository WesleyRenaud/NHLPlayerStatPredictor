from pathlib import Path

import pytest

from api.paths import Paths
from api.recency.pim_multiplier_store import PimMultiplierStore
from api.recency.production_growth import ProductionGrowth
from api.recency.production_multiplier_store import ProductionMultiplierStore
from api.recency.scoring_multiplier_store import ScoringMultiplierStore
from api.recency.shots_multiplier_store import ShotsMultiplierStore


@pytest.mark.parametrize( 'store', [ ScoringMultiplierStore, PimMultiplierStore, ShotsMultiplierStore ] )
def Test_Write_TestMultipliers_ExpectIndependentTypedRoundTrip(
      store: type[ ProductionMultiplierStore ],
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   growth = [ ProductionGrowth( 18, 19, 1.2, 30 ) ]

   store.write( growth )

   assert store.read() == growth
   assert list( tmp_path.iterdir() ) == [ store.path() ]
