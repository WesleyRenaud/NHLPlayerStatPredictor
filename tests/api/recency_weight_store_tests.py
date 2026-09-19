from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.paths import Paths
from api.recency_weight import RecencyWeight
from api.recency_weight_store import RecencyWeightStore


def Test_Write_TestWeights_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   weights = [ RecencyWeight( 0, 0.75 ), RecencyWeight( 1, 0.25 ) ]
   RecencyWeightStore.write( weights )
   assert RecencyWeightStore.read() == weights
   assert RecencyWeightStore.path().read_text() == json.dumps(
      [ weight.to_dict() for weight in weights ],
      indent=2 )
   assert RecencyWeightStore.path() == tmp_path / RecencyWeightStore.FILE_NAME
