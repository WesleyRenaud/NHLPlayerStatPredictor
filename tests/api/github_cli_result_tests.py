from __future__ import annotations

from api.github_cli_result import GithubCliResult
from api.position import Position


def Test_Equality_TestSameFields_ExpectEqual() -> None:
   result = GithubCliResult( Position.FIRST, 'ok', '' )
   assert result == GithubCliResult( Position.FIRST, 'ok', '' )
   assert result in { GithubCliResult( Position.FIRST, 'ok', '' ) }
