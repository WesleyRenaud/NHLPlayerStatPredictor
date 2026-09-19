from __future__ import annotations

from .nhl_client import NhlClient
from .shared.enums.position import Position


class RecencyTargetResolver():
   @classmethod
   def resolve( cls ) -> int:
      return sorted( NhlClient.seasons() )[ Position.LAST ].season_id
