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


def Test_Ingest_TestRun_ExpectForcedIngesterMain( monkeypatch: pytest.MonkeyPatch ) -> None:
   forced: list[ bool ] = []

   def fake_main( force: bool = False ) -> None:
      forced.append( force )

   monkeypatch.setattr( sys, 'argv', [ 'api', 'ingest' ] )
   monkeypatch.setattr( app_runner.SkaterSeasonIngester, 'main', fake_main )
   AppRunner.run()
   assert forced == [ True ]


def Test_Pull_TestRun_ExpectArtifactPullerMain( monkeypatch: pytest.MonkeyPatch ) -> None:
   called: list[ bool ] = []

   monkeypatch.setattr( sys, 'argv', [ 'api', AppRunner.pull.__name__ ] )
   monkeypatch.setattr( app_runner.IngestArtifactPuller, 'main', lambda: called.append( True ) )
   AppRunner.run()
   assert called == [ True ]


def Test_Start_TestRun_ExpectSyncThenServer( monkeypatch: pytest.MonkeyPatch ) -> None:
   events: list[ str ] = []
   sync_name = app_runner.IngestArtifactPuller.sync.__name__
   run_name = app_runner.ServerRunner.run.__name__

   monkeypatch.setattr(
      app_runner.IngestArtifactPuller,
      'sync',
      lambda: events.append( sync_name ) )
   monkeypatch.setattr(
      app_runner.ServerRunner,
      'run',
      lambda: events.append( run_name ) )
   AppRunner.start()
   assert events == [ sync_name, run_name ]


def Test_Run_TestRunName_ExpectStartsServer( monkeypatch: pytest.MonkeyPatch ) -> None:
   called: list[ bool ] = []

   monkeypatch.setattr( sys, 'argv', [ 'api', AppRunner.run.__name__ ] )
   monkeypatch.setattr( app_runner.IngestArtifactPuller, 'sync', lambda: None )
   monkeypatch.setattr( app_runner.ServerRunner, 'run', lambda: called.append( True ) )
   AppRunner.run()
   assert called == [ True ]
