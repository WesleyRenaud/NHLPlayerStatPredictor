from __future__ import annotations

from api.availability.games_share import GamesShare


def Test_Resolve_TestGamesAndSeasonLength_ExpectShare() -> None:
   season_length = 82
   games = season_length // 2

   share = GamesShare.resolve( games, season_length )

   assert share == games / season_length
