from __future__ import annotations

from ..ingest.json_file_cache import JsonFileCache
from .usable_nhl_ice import UsableNhlIce
from .usable_nhl_ice_resolver import UsableNhlIceResolver


class ClubIceProvider():
   @classmethod
   def resolve( cls, player_id: int ) -> UsableNhlIce | None:
      return UsableNhlIceResolver.resolve(
         JsonFileCache().read_object( f'player_landing_{ player_id }' ) or {} )
