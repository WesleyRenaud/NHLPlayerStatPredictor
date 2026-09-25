from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.depth.slot_chosen_share import SlotChosenShare
from api.depth.slot_chosen_share_store import SlotChosenShareStore
from api.paths import Paths
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup


def Test_Write_TestShares_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   shares = [ SlotChosenShare( 12, SkaterGroup( 'F' ), 0.5, 0.56 ) ]
   SlotChosenShareStore.write( shares )
   assert SlotChosenShareStore.read() == [
      SlotChosenShare.from_row( shares[ Position.FIRST ].to_dict() )
   ]
   assert SlotChosenShareStore.path().read_text() == json.dumps(
      [ shares[ Position.FIRST ].to_dict() ],
      indent=2 )


def Test_Read_TestMissing_ExpectEmpty(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   assert SlotChosenShareStore.read() == []
