from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.depth.slot_average import SlotAverage
from api.depth.slot_average_store import SlotAverageStore
from api.paths import Paths
from api.shared.enums.position import Position


def Test_Write_TestSlots_ExpectReadable(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   slots = [ SlotAverage( 7, 14.9, 2.6, 12.4 ) ]
   SlotAverageStore.write( slots )

   loaded = SlotAverageStore.read()
   written = SlotAverageStore.path().read_text()

   assert loaded == slots
   assert written == json.dumps(
      [ slots[ Position.FIRST ].to_dict() ],
      indent=2 )


def Test_Read_TestMissing_ExpectEmpty(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )

   slots = SlotAverageStore.read()

   assert slots == []
