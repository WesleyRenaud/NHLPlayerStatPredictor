from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.paths import Paths
from api.recency.age_recency_weights import AgeRecencyWeights
from api.recency.recency_weight import RecencyWeight
from api.recency.scoring_weight_store import ScoringWeightStore


def Test_Write_TestWeights_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   weights = [
      AgeRecencyWeights( 19, [ RecencyWeight( 0, 1.0 ), RecencyWeight( 1, 0.0 ) ] )
   ]
   ScoringWeightStore.write( weights )

   loaded = ScoringWeightStore.read()
   written = ScoringWeightStore.path().read_text()

   assert loaded == weights
   assert written == json.dumps(
      [ weight.to_dict() for weight in weights ],
      indent=2 )
   assert ScoringWeightStore.path() == tmp_path / ScoringWeightStore.FILE_NAME
