from __future__ import annotations

from pathlib import Path

from api.ingest.json_file_cache import JsonFileCache
from api.shared.enums.position import Position
from api.types import Types


def Test_ReadList_TestMissingFile_ExpectNone( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   name = 'seasons'

   stored = cache.read_list( name )

   assert stored is None


def Test_WriteList_TestRows_ExpectReadable( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   name = 'seasons'
   rows = [ { 'id': 1 } ]
   cache.write_list( name, rows )

   stored = cache.read_list( name )

   assert stored == rows


def Test_ReadList_TestNonListPayload_ExpectEmptyList( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   name = 'seasons'
   ( tmp_path / f'{ name }.json' ).write_text( '{"id": 1}' )

   stored = cache.read_list( name )

   assert stored == []


def Test_GetList_TestMissingFile_ExpectFetchedRows( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   name = 'seasons'
   fetched_rows = [ { 'id': 1 } ]
   calls: list[ int ] = []

   def fetch() -> Types.JsonObjectList:
      calls.append( Position.SECOND )
      return fetched_rows

   stored = cache.get_list( name, fetch )
   cached = cache.read_list( name )

   assert stored == fetched_rows
   assert calls == [ Position.SECOND ]
   assert cached == fetched_rows


def Test_GetList_TestCachedFile_ExpectFetchSkipped( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   name = 'seasons'
   cached_rows = [ { 'id': 1 } ]
   fetched_rows = [ { 'id': 2 } ]
   cache.write_list( name, cached_rows )

   def fetch() -> Types.JsonObjectList:
      return fetched_rows

   stored = cache.get_list( name, fetch )

   assert stored == cached_rows


def Test_GetList_TestForce_ExpectFetchedRows( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   name = 'seasons'
   cached_rows = [ { 'id': 1 } ]
   fetched_rows = [ { 'id': 2 } ]
   cache.write_list( name, cached_rows )

   def fetch() -> Types.JsonObjectList:
      return fetched_rows

   stored = cache.get_list( name, fetch, force=True )
   cached = cache.read_list( name )

   assert stored == fetched_rows
   assert cached == fetched_rows


def Test_GetObject_TestMissingFile_ExpectFetchedPayload( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   name = 'landing'
   fetched_payload = { 'id': 1 }
   calls: list[ int ] = []

   def fetch() -> Types.JsonObject:
      calls.append( Position.SECOND )
      return fetched_payload

   stored = cache.get_object( name, fetch )
   cached = cache.read_object( name )

   assert stored == fetched_payload
   assert calls == [ Position.SECOND ]
   assert cached == fetched_payload


def Test_GetObject_TestCachedFile_ExpectFetchSkipped( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   name = 'landing'
   cached_payload = { 'id': 1 }
   fetched_payload = { 'id': 2 }
   cache.write_object( name, cached_payload )

   def fetch() -> Types.JsonObject:
      return fetched_payload

   stored = cache.get_object( name, fetch )

   assert stored == cached_payload


def Test_ReadObject_TestNonObjectPayload_ExpectEmptyObject( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   name = 'landing'
   ( tmp_path / f'{ name }.json' ).write_text( '[]' )

   stored = cache.read_object( name )

   assert stored == {}
