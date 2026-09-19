from __future__ import annotations

import json
import time

import httpx

from .types import Types


class JsonHttpClient():
   USER_AGENT = 'NHLPlayerStatPredictor/0.1 (local research tool)'
   TIMEOUT = 30.0
   MAX_ATTEMPTS = 6
   RETRY_DELAY_SECONDS = 1.5
   RETRY_STATUS_CODES = { 429, 500, 502, 503, 504 }

   @classmethod
   def get_json(
         cls,
         url: str,
         params: dict[ str, str | int ] | None = None ) -> Types.JsonObject | Types.JsonObjectList:
      last_error: Exception | None = None
      http_client = httpx.Client(
         timeout=JsonHttpClient.TIMEOUT,
         headers={ 'User-Agent': JsonHttpClient.USER_AGENT, 'Accept': 'application/json' },
         follow_redirects=True )

      try:
         for attempt in range( JsonHttpClient.MAX_ATTEMPTS ):
            try:
               response = http_client.get( url, params=params )

               if response.status_code in JsonHttpClient.RETRY_STATUS_CODES:
                  time.sleep( JsonHttpClient.RETRY_DELAY_SECONDS * ( attempt + 1 ) )
                  continue

               response.raise_for_status()
               payload = response.json()

               if isinstance( payload, dict ):
                  return payload

               if isinstance( payload, list ):
                  return [ row for row in payload if isinstance( row, dict ) ]

               raise RuntimeError( f'Unexpected JSON payload from { url }' )
            except ( httpx.HTTPError, json.JSONDecodeError ) as exc:
               last_error = exc
               time.sleep( JsonHttpClient.RETRY_DELAY_SECONDS * ( attempt + 1 ) )
      finally:
         http_client.close()

      raise RuntimeError( f'Failed GET { url }' ) from last_error
