from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.depth.ice_chosen_share import IceChosenShare
from api.depth.ice_chosen_share_store import IceChosenShareStore
from api.paths import Paths
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup


def Test_Write_TestShares_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   shares = [ IceChosenShare( 18.0, SkaterGroup( 'D' ), 0.5, 0.56 ) ]
   IceChosenShareStore.write( shares )

   loaded = IceChosenShareStore.read()
   written = IceChosenShareStore.path().read_text()

   assert loaded == shares
   assert written == json.dumps(
      [ shares[ Position.FIRST ].to_dict() ],
      indent=2 )


def Test_Read_TestMissing_ExpectEmpty(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )

   shares = IceChosenShareStore.read()

   assert shares == []
