from __future__ import annotations

from pathlib import Path
import sqlite3

from api.seed.schema_creator import SchemaCreator
from api.shared.enums.position import Position


def Test_Create_TestNewDatabase_ExpectSkaterSeasonsTable( tmp_path: Path ) -> None:
   conn = sqlite3.connect( str( tmp_path / 'skaters.sqlite' ) )

   try:
      SchemaCreator.create( conn.cursor() )
      tables = {
         row[ Position.FIRST ]
         for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'" )
      }
      indexes = {
         row[ Position.FIRST ]
         for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'" )
      }
   finally:
      conn.close()

   user_tables = { name for name in tables if not name.startswith( 'sqlite_' ) }
   user_indexes = { name for name in indexes if not name.startswith( 'sqlite_' ) }

   assert user_tables
   assert user_indexes
