from __future__ import annotations

from .club_ice import ClubIce
from ..ingest.club_ice_parser import ClubIceParser
from ..ingest.json_file_cache import JsonFileCache


class ClubIceProvider():
   @classmethod
   def resolve( cls, player_id: int, season_id: int ) -> list[ ClubIce ]:
      return ClubIceParser.parse(
         JsonFileCache().read_object( f'player_landing_{ player_id }' ) or {},
         season_id )
