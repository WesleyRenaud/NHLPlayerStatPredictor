from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.paths import Paths
from api.shared.enums.position import Position
from api.team import Team
from api.team_factor import TeamFactor
from api.team_factor_skater import TeamFactorSkater
from api.team_factor_store import TeamFactorStore


def Test_Write_TestFactors_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   factors = [
      TeamFactor(
         20252026,
         list( Team )[ Position.FIRST ],
         0.87,
         [ TeamFactorSkater( 97, 120.5 ) ] ),
      TeamFactor(
         20262027,
         list( Team )[ Position.SECOND ],
         1.12,
         [ TeamFactorSkater( 29, 88.0 ) ] ),
   ]
   TeamFactorStore.write( factors )
   assert TeamFactorStore.read() == factors
   assert TeamFactorStore.path().read_text() == json.dumps(
      [ factor.to_dict() for factor in factors ],
      indent=2 )
   assert TeamFactorStore.path() == tmp_path / TeamFactorStore.FILE_NAME
