from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

import api.github_cli as github_cli
from api.github_cli import GithubCli
from api.github_cli_result import GithubCliResult
from api.position import Position


def Test_Run_TestSuccess_ExpectStdout( monkeypatch: pytest.MonkeyPatch ) -> None:
   def fake_run(
         command: list[ str ],
         check: bool,
         capture_output: bool,
         text: bool,
         cwd: Path ) -> subprocess.CompletedProcess[ str ]:
      assert command[ Position.FIRST ] == GithubCli.PROGRAM
      return subprocess.CompletedProcess(
         command,
         Position.FIRST,
         stdout='ok',
         stderr='' )

   monkeypatch.setattr( github_cli.subprocess, 'run', fake_run )
   assert GithubCli.run( [ 'status' ] ) == 'ok'


def Test_Run_TestFailure_ExpectSystemExit( monkeypatch: pytest.MonkeyPatch ) -> None:
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
         stderr='failed' )

   monkeypatch.setattr( github_cli.subprocess, 'run', fake_run )

   with pytest.raises( SystemExit ) as exit_info:
      GithubCli.run( [ 'status' ] )

   assert exit_info.value.code == Position.SECOND


def Test_Run_TestMissingProgram_ExpectSystemExit(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   def fake_run(
         command: list[ str ],
         check: bool,
         capture_output: bool,
         text: bool,
         cwd: Path ) -> subprocess.CompletedProcess[ str ]:
      raise FileNotFoundError()

   monkeypatch.setattr( github_cli.subprocess, 'run', fake_run )

   with pytest.raises( SystemExit ) as exit_info:
      GithubCli.run( [ 'status' ] )

   assert exit_info.value.code == Position.SECOND


def Test_Invoke_TestMissingProgram_ExpectFailedResult(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   def fake_run(
         command: list[ str ],
         check: bool,
         capture_output: bool,
         text: bool,
         cwd: Path ) -> subprocess.CompletedProcess[ str ]:
      raise FileNotFoundError()

   monkeypatch.setattr( github_cli.subprocess, 'run', fake_run )
   result = GithubCli.invoke( [ 'status' ] )
   assert result == GithubCliResult( Position.SECOND, '', '' )
