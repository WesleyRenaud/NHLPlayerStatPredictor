from __future__ import annotations

from api.ingest.github_cli_result import GithubCliResult
from api.shared.enums.position import Position


def Test_Equality_TestSameFields_ExpectEqual() -> None:
   code = Position.FIRST
   stdout = 'ok'
   stderr = ''
   result = GithubCliResult( code, stdout, stderr )
   other = GithubCliResult( code, stdout, stderr )

   assert result == other
   assert result in { other }
