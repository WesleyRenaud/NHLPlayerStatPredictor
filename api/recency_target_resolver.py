from __future__ import annotations

from .ingest.nhl_client import NhlClient
from .season import Season
from .season_length import SeasonLength


class RecencyTargetResolver():
   @classmethod
   def season( cls ) -> SeasonLength:
      return Season.latest( NhlClient.seasons() )


   @classmethod
   def resolve( cls ) -> int:
      return cls.season().season_id


   @classmethod
   def prior( cls ) -> int:
      return Season.prior( NhlClient.seasons() ).season_id
