from __future__ import annotations

import sqlite3

from .paths import Paths
from .types import Types


class DatabaseConnectionProvider():
   @classmethod
   def open( cls, db_path: str ) -> Types.Connection:
      Paths.PROCESSED_DIR.mkdir( parents=True, exist_ok=True )
      conn = sqlite3.connect( db_path )
      conn.row_factory = sqlite3.Row
      return conn


   @classmethod
   def close( cls, conn: Types.Connection | None ) -> None:
      if conn is None:
         return

      conn.close()


   @classmethod
   def rows(
         cls,
         db_path: str,
         sql: str,
         parameters: list[ int ] | None = None ) -> list[ Types.Row ]:
      conn = cls.open( db_path )

      try:
         return list( conn.execute( sql, parameters or [] ).fetchall() )
      finally:
         cls.close( conn )
