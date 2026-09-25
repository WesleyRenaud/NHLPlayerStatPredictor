from __future__ import annotations

from .ingest.nhl_client import NhlClient
from .season import Season


class RecencyTargetResolver():
   @classmethod
   def resolve( cls ) -> int:
      return Season.latest( NhlClient.seasons() ).season_id


   @classmethod
   def prior( cls ) -> int:
      return Season.prior( NhlClient.seasons() ).season_id
