from __future__ import annotations

from collections.abc import Callable
from datetime import date

from .nhl_client import NhlClient


class SeasonGames():
   @classmethod
   def played( cls, season_id: int, on_date: date, games: Callable[ [], int ] ) -> int:
      season = next( row for row in NhlClient.seasons() if row.season_id == season_id )

      if on_date < season.start_date:
         return 0

      return games()
