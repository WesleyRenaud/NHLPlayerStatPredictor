from __future__ import annotations

import sys

import pytest

import api.app_runner as app_runner
from api.app_runner import AppRunner
from api.position import Position


def Test_Lookup_TestMissingName_ExpectUsageError( monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr( sys, 'argv', [ 'api', 'lookup' ] )

   with pytest.raises( SystemExit ) as exit_info:
      AppRunner.lookup()

   assert exit_info.value.code == Position.SECOND


def Test_Run_TestUnknownName_ExpectUsageError( monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr( sys, 'argv', [ 'api', 'unknown' ] )

   with pytest.raises( SystemExit ) as exit_info:
      AppRunner.run()

   assert exit_info.value.code == Position.SECOND


def Test_Ingest_TestRun_ExpectIngesterMain( monkeypatch: pytest.MonkeyPatch ) -> None:
   called: list[ bool ] = []

   def fake_main() -> None:
      called.append( True )

   monkeypatch.setattr( sys, 'argv', [ 'api', 'ingest' ] )
   monkeypatch.setattr( app_runner.SkaterSeasonIngester, 'main', fake_main )
   AppRunner.run()
   assert called == [ True ]
