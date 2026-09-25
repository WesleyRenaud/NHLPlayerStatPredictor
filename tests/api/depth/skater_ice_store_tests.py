from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.depth.skater_ice import SkaterIce
from api.depth.skater_ice_store import SkaterIceStore
from api.paths import Paths
from api.shared.enums.position import Position


def Test_Write_TestRows_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   rows = [ SkaterIce( 97, 21.5, 22.0 ) ]
   SkaterIceStore.write( rows )
   assert SkaterIceStore.read() == [
      SkaterIce.from_row( rows[ Position.FIRST ].to_dict() )
   ]
   assert SkaterIceStore.by_player() == { 97: SkaterIceStore.read()[ Position.FIRST ] }
   assert SkaterIceStore.path().read_text() == json.dumps(
      [ rows[ Position.FIRST ].to_dict() ],
      indent=2 )


def Test_Read_TestMissing_ExpectEmpty(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   assert SkaterIceStore.read() == []
   assert SkaterIceStore.by_player() == {}
