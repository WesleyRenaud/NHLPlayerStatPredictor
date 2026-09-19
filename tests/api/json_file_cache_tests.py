from __future__ import annotations

from pathlib import Path

from api.json_file_cache import JsonFileCache
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
      calls.append( 1 )
      return [ { 'id': 1 } ]

   cache = JsonFileCache( tmp_path )
   assert cache.get_list( 'seasons', fetch ) == [ { 'id': 1 } ]
   assert calls == [ 1 ]
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
