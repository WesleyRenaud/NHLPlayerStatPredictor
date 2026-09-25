from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.aging.aging_factor import AgingFactor
from api.aging.aging_factor_store import AgingFactorStore
from api.paths import Paths


def Test_Write_TestFactors_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   factors = [ AgingFactor( 24, -0.009, 0.002 ), AgingFactor( 28, -0.07, -0.044 ) ]
   AgingFactorStore.write( factors )

   loaded = AgingFactorStore.read()
   written = AgingFactorStore.path().read_text()

   assert loaded == factors
   assert written == json.dumps(
      [ factor.to_dict() for factor in factors ],
      indent=2 )
   assert AgingFactorStore.path() == tmp_path / AgingFactorStore.FILE_NAME
