from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.aging.league_arrival import LeagueArrival
from api.aging.league_arrival_store import LeagueArrivalStore
from api.paths import Paths


def Test_Read_TestMissingFile_ExpectNoArrivals( monkeypatch: pytest.MonkeyPatch, tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )

   assert LeagueArrivalStore.read() == []


def Test_Write_TestArrivals_ExpectReadable( monkeypatch: pytest.MonkeyPatch, tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   arrivals = [ LeagueArrival( 'AAA', 18, 0.9 ) ]
   LeagueArrivalStore.write( arrivals )

   assert LeagueArrivalStore.read() == arrivals
   assert LeagueArrivalStore.path().read_text() == json.dumps(
      [ arrival.to_dict() for arrival in arrivals ],
      indent=2 )
