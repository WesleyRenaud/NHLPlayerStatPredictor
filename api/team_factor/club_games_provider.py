from __future__ import annotations

from .club_games import ClubGames
from ..ingest.club_games_parser import ClubGamesParser
from ..ingest.json_file_cache import JsonFileCache


class ClubGamesProvider():
   @classmethod
   def resolve( cls, player_id: int, season_id: int ) -> list[ ClubGames ]:
      return ClubGamesParser.parse(
         JsonFileCache().read_object( f'player_landing_{ player_id }' ) or {},
         season_id )
