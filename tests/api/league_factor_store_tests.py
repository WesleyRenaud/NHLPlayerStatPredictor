from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.league_factor import LeagueFactor
from api.league_factor_store import LeagueFactorStore
from api.paths import Paths


def Test_Write_TestFactors_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   factors = [ LeagueFactor( 'AAA', 0.44, 0.42 ), LeagueFactor( 'BBB', 0.28, 0.30 ) ]
   LeagueFactorStore.write( factors )
   assert LeagueFactorStore.read() == factors
   assert LeagueFactorStore.path().read_text() == json.dumps(
      [ factor.to_dict() for factor in factors ],
      indent=2 )
   assert LeagueFactorStore.path() == tmp_path / LeagueFactorStore.FILE_NAME
