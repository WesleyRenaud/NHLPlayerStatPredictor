from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

import api.ingest.github_cli as github_cli
from api.ingest.github_cli import GithubCli
from api.ingest.github_cli_result import GithubCliResult
from api.shared.enums.position import Position


def Test_Run_TestSuccess_ExpectStdout( monkeypatch: pytest.MonkeyPatch ) -> None:
   args = [ 'status' ]
   stdout = 'ok'
   captured: list[ list[ str ] ] = []

   def fake_run(
         command: list[ str ],
         check: bool,
         capture_output: bool,
         text: bool,
         cwd: Path ) -> subprocess.CompletedProcess[ str ]:
      captured.append( command )
      return subprocess.CompletedProcess(
         command,
         Position.FIRST,
         stdout=stdout,
         stderr='' )

   monkeypatch.setattr( github_cli.subprocess, 'run', fake_run )

   result = GithubCli.run( args )

   assert result == stdout
   assert captured[ Position.FIRST ][ Position.FIRST ] == GithubCli.PROGRAM


def Test_Run_TestFailure_ExpectSystemExit( monkeypatch: pytest.MonkeyPatch ) -> None:
   args = [ 'status' ]
   stderr = 'failed'

   def fake_run(
         command: list[ str ],
         check: bool,
         capture_output: bool,
         text: bool,
         cwd: Path ) -> subprocess.CompletedProcess[ str ]:
      return subprocess.CompletedProcess(
         command,
         Position.SECOND,
         stdout='',
         stderr=stderr )

   monkeypatch.setattr( github_cli.subprocess, 'run', fake_run )

   with pytest.raises( SystemExit ) as exit_info:
      GithubCli.run( args )

   assert exit_info.value.code == Position.SECOND


def Test_Run_TestMissingProgram_ExpectSystemExit(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   args = [ 'status' ]

   def fake_run(
         command: list[ str ],
         check: bool,
         capture_output: bool,
         text: bool,
         cwd: Path ) -> subprocess.CompletedProcess[ str ]:
      raise FileNotFoundError()

   monkeypatch.setattr( github_cli.subprocess, 'run', fake_run )

   with pytest.raises( SystemExit ) as exit_info:
      GithubCli.run( args )

   assert exit_info.value.code == Position.SECOND


def Test_Invoke_TestMissingProgram_ExpectFailedResult(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   args = [ 'status' ]

   def fake_run(
         command: list[ str ],
         check: bool,
         capture_output: bool,
         text: bool,
         cwd: Path ) -> subprocess.CompletedProcess[ str ]:
      raise FileNotFoundError()

   monkeypatch.setattr( github_cli.subprocess, 'run', fake_run )

   result = GithubCli.invoke( args )

   assert result == GithubCliResult( Position.SECOND, '', '' )
