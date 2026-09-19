from __future__ import annotations

from .nhl_client import NhlClient
from .season import Season


class PaceGamesResolver():
   @classmethod
   def resolve( cls ) -> int:
      return Season.pace_games( NhlClient.seasons() )
