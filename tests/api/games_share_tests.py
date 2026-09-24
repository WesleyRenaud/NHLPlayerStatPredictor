from __future__ import annotations

from api.games_share import GamesShare


def Test_Resolve_TestGamesAndSeasonLength_ExpectShare() -> None:
   assert GamesShare.resolve( 41, 82 ) == 0.5
