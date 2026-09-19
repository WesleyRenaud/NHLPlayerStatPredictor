from __future__ import annotations

from .json_file_cache import JsonFileCache
from .json_http_client import JsonHttpClient
from .season_length import SeasonLength
from .skater_bio import SkaterBio
from .skater_summary import SkaterSummary
from .types import Types


class NhlClient():
   STATS_BASE = 'https://api.nhle.com/stats/rest/en'
   PAGE_SIZE = 100
   REGULAR_SEASON_GAME_TYPE_ID = 2

   @classmethod
   def seasons( cls, force: bool = False ) -> list[ SeasonLength ]:
      return SeasonLength.from_rows(
         JsonFileCache().get_list( 'seasons', cls._fetch_seasons, force ) )


   @classmethod
   def skater_summary( cls, season_id: int, force: bool = False ) -> list[ SkaterSummary ]:
      return SkaterSummary.from_rows( cls._skater_report( 'summary', season_id, force ) )


   @classmethod
   def skater_bios( cls, season_id: int, force: bool = False ) -> list[ SkaterBio ]:
      return SkaterBio.from_rows( cls._skater_report( 'bios', season_id, force ) )


   @classmethod
   def _skater_report(
         cls,
         report: str,
         season_id: int,
         force: bool ) -> Types.JsonObjectList:
      return JsonFileCache().get_list(
         f'skater_{ report }_{ season_id }',
         lambda: cls._fetch_skater_report( report, season_id ),
         force )


   @classmethod
   def _fetch_skater_report(
         cls,
         report: str,
         season_id: int ) -> Types.JsonObjectList:
      return cls._fetch_all_rows(
         f'{ NhlClient.STATS_BASE }/skater/{ report }',
         (
            f'gameTypeId={ NhlClient.REGULAR_SEASON_GAME_TYPE_ID } '
            f'and seasonId={ season_id }' ) )


   @classmethod
   def _fetch_seasons( cls ) -> Types.JsonObjectList:
      return cls._data_rows(
         JsonHttpClient.get_json( f'{ NhlClient.STATS_BASE }/season' ) )


   @classmethod
   def _fetch_all_rows(
         cls,
         report_url: str,
         cayenne_exp: str ) -> Types.JsonObjectList:
      rows: Types.JsonObjectList = []
      start = 0
      total: int | None = None

      while total is None or start < total:
         payload = JsonHttpClient.get_json(
            report_url,
            params=cls._page_params( start, cayenne_exp ) )
         batch = cls._data_rows( payload )
         total = cls._total( payload )

         if not batch:
            break

         rows.extend( batch )
         start += len( batch )

      return rows


   @classmethod
   def _page_params(
         cls,
         start: int,
         cayenne_exp: str ) -> dict[ str, str | int ]:
      return {
         'isAggregate': 'false',
         'isGame': 'false',
         'start': start,
         'limit': NhlClient.PAGE_SIZE,
         'sort': 'playerId',
         'cayenneExp': cayenne_exp,
      }


   @classmethod
   def _data_rows(
         cls,
         payload: Types.JsonObject | Types.JsonObjectList ) -> Types.JsonObjectList:
      if not isinstance( payload, dict ):
         return []

      raw_rows = payload.get( 'data' ) or []

      if not isinstance( raw_rows, list ):
         return []

      return [ row for row in raw_rows if isinstance( row, dict ) ]


   @classmethod
   def _total(
         cls,
         payload: Types.JsonObject | Types.JsonObjectList ) -> int:
      if not isinstance( payload, dict ):
         return 0

      return int( payload.get( 'total' ) or 0 )
