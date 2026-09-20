from __future__ import annotations

from concurrent.futures import as_completed, ThreadPoolExecutor

from .nhl_client import NhlClient
from .types import Types


class PlayerLandingFetcher():
   WORKERS = 16
   PROGRESS_EVERY = 100


   @classmethod
   def fetch(
         cls,
         player_ids: list[ int ],
         force: bool = False ) -> dict[ int, Types.JsonObject ]:
      completed: dict[ int, Types.JsonObject ] = {}
      total = len( player_ids )
      finished = 0

      with ThreadPoolExecutor( max_workers=PlayerLandingFetcher.WORKERS ) as executor:
         futures = {
            executor.submit( cls._landing, player_id, force ): player_id
            for player_id in player_ids
         }

         for future in as_completed( futures ):
            player_id = futures[ future ]
            landing = future.result()
            finished += 1

            if landing is not None:
               completed[ player_id ] = landing

            if (
                  finished == 1
                  or finished % PlayerLandingFetcher.PROGRESS_EVERY == 0
                  or finished == total ):
               print( f'Fetching landings { finished }/{ total }...', flush=True )

      return {
         player_id: completed[ player_id ]
         for player_id in player_ids
         if player_id in completed
      }


   @classmethod
   def _landing(
         cls,
         player_id: int,
         force: bool ) -> Types.JsonObject | None:
      try:
         return NhlClient.player_landing( player_id, force=force )
      except RuntimeError:
         return None
