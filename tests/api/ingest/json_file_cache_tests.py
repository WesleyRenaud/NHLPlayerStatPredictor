from __future__ import annotations

from pathlib import Path

from api.ingest.json_file_cache import JsonFileCache
from api.shared.enums.position import Position
from api.types import Types


def Test_ReadList_TestMissingFile_ExpectNone( tmp_path: Path ) -> None:
   assert JsonFileCache( tmp_path ).read_list( 'seasons' ) is None


def Test_WriteList_TestRows_ExpectReadable( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   rows = [ { 'id': 1 } ]
   cache.write_list( 'seasons', rows )
   assert cache.read_list( 'seasons' ) == rows


def Test_ReadList_TestNonListPayload_ExpectEmptyList( tmp_path: Path ) -> None:
   ( tmp_path / 'seasons.json' ).write_text( '{"id": 1}' )
   assert JsonFileCache( tmp_path ).read_list( 'seasons' ) == []


def Test_GetList_TestMissingFile_ExpectFetchedRows( tmp_path: Path ) -> None:
   calls: list[ int ] = []

   def fetch() -> Types.JsonObjectList:
      calls.append( Position.SECOND )
      return [ { 'id': 1 } ]

   cache = JsonFileCache( tmp_path )
   assert cache.get_list( 'seasons', fetch ) == [ { 'id': 1 } ]
   assert calls == [ Position.SECOND ]
   assert cache.read_list( 'seasons' ) == [ { 'id': 1 } ]


def Test_GetList_TestCachedFile_ExpectFetchSkipped( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   cache.write_list( 'seasons', [ { 'id': 1 } ] )

   def fetch() -> Types.JsonObjectList:
      return [ { 'id': 2 } ]

   assert cache.get_list( 'seasons', fetch ) == [ { 'id': 1 } ]


def Test_GetList_TestForce_ExpectFetchedRows( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   cache.write_list( 'seasons', [ { 'id': 1 } ] )

   def fetch() -> Types.JsonObjectList:
      return [ { 'id': 2 } ]

   assert cache.get_list( 'seasons', fetch, force=True ) == [ { 'id': 2 } ]
   assert cache.read_list( 'seasons' ) == [ { 'id': 2 } ]


def Test_GetObject_TestMissingFile_ExpectFetchedPayload( tmp_path: Path ) -> None:
   calls: list[ int ] = []

   def fetch() -> Types.JsonObject:
      calls.append( Position.SECOND )
      return { 'id': 1 }

   cache = JsonFileCache( tmp_path )
   assert cache.get_object( 'landing', fetch ) == { 'id': 1 }
   assert calls == [ Position.SECOND ]
   assert cache.read_object( 'landing' ) == { 'id': 1 }


def Test_GetObject_TestCachedFile_ExpectFetchSkipped( tmp_path: Path ) -> None:
   cache = JsonFileCache( tmp_path )
   cache.write_object( 'landing', { 'id': 1 } )

   def fetch() -> Types.JsonObject:
      return { 'id': 2 }

   assert cache.get_object( 'landing', fetch ) == { 'id': 1 }


def Test_ReadObject_TestNonObjectPayload_ExpectEmptyObject( tmp_path: Path ) -> None:
   ( tmp_path / 'landing.json' ).write_text( '[]' )
   assert JsonFileCache( tmp_path ).read_object( 'landing' ) == {}
