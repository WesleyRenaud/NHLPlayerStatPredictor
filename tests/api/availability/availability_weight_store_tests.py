from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.availability.availability_weight_store import AvailabilityWeightStore
from api.paths import Paths
from api.recency.recency_weight import RecencyWeight


def Test_Write_TestWeights_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   weights = [ RecencyWeight( 0, 0.75 ), RecencyWeight( 1, 0.25 ) ]
   AvailabilityWeightStore.write( weights )
   assert AvailabilityWeightStore.read() == weights
   assert AvailabilityWeightStore.path().read_text() == json.dumps(
      [ weight.to_dict() for weight in weights ],
      indent=2 )
   assert AvailabilityWeightStore.path() == tmp_path / AvailabilityWeightStore.FILE_NAME
