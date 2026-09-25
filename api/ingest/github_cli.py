from __future__ import annotations

import subprocess

from .github_cli_result import GithubCliResult
from ..paths import Paths
from ..shared.enums.position import Position


class GithubCli():
   PROGRAM = 'gh'

   @classmethod
   def invoke( cls, args: list[ str ] ) -> GithubCliResult:
      try:
         completed = subprocess.run(
            [ cls.PROGRAM, *args ],
            check=False,
            capture_output=True,
            text=True,
            cwd=Paths.ROOT )
      except FileNotFoundError:
         return GithubCliResult( Position.SECOND, '', '' )

      return GithubCliResult( completed.returncode, completed.stdout, completed.stderr )


   @classmethod
   def run( cls, args: list[ str ] ) -> str:
      result = cls.invoke( args )

      if result.returncode != Position.FIRST:
         print( result.stderr )
         raise SystemExit( Position.SECOND )

      return result.stdout
