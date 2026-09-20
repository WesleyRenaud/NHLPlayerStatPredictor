from __future__ import annotations

from collections.abc import Callable
import json
from pathlib import Path

from .paths import Paths
from .types import Types


class JsonFileCache():
   def __init__( self, directory: Path | None = None ) -> None:
      self._directory = directory if directory is not None else Paths.RAW_DIR


   def get_list(
         self,
         name: str,
         fetch: Callable[ [ ], Types.JsonObjectList ],
         force: bool = False ) -> Types.JsonObjectList:
      if not force:
         cached = self.read_list( name )

         if cached is not None:
            return cached

      rows = fetch()
      self.write_list( name, rows )
      return rows


   def read_list( self, name: str ) -> Types.JsonObjectList | None:
      path = self._path( name )

      if not path.exists():
         return None

      payload = json.loads( path.read_text() )
      return payload if isinstance( payload, list ) else []


   def write_list( self, name: str, rows: Types.JsonObjectList ) -> None:
      path = self._path( name )
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text( json.dumps( rows ) )


   def get_object(
         self,
         name: str,
         fetch: Callable[ [ ], Types.JsonObject ],
         force: bool = False ) -> Types.JsonObject:
      if not force:
         cached = self.read_object( name )

         if cached is not None:
            return cached

      payload = fetch()
      self.write_object( name, payload )
      return payload


   def read_object( self, name: str ) -> Types.JsonObject | None:
      path = self._path( name )

      if not path.exists():
         return None

      payload = json.loads( path.read_text() )
      return payload if isinstance( payload, dict ) else {}


   def write_object( self, name: str, payload: Types.JsonObject ) -> None:
      path = self._path( name )
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text( json.dumps( payload ) )


   def _path( self, name: str ) -> Path:
      return self._directory / f'{ name }.json'
