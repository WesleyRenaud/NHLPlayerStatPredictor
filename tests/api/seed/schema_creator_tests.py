from __future__ import annotations

from pathlib import Path
import sqlite3

from api.position import Position
from api.seed.schema_creator import SchemaCreator


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

   assert 'SkaterSeason' in tables
   assert 'SkaterSeasonNameIndex' in indexes
