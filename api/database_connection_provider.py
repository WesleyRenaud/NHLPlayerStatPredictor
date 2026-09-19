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
