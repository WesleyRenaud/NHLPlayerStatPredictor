from __future__ import annotations

from pathlib import Path
import sqlite3

from api.seed.tables.roster_skater_seed_table import RosterSkaterSeedTable
from api.shared.enums.position import Position


def Test_CreateTable_TestNewDatabase_ExpectUserTable( tmp_path: Path ) -> None:
   conn = sqlite3.connect( str( tmp_path / 'skaters.sqlite' ) )

   try:
      RosterSkaterSeedTable.create_table( conn.cursor() )
      names = {
         row[ Position.FIRST ]
         for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'" )
      }
   finally:
      conn.close()

   user_tables = { name for name in names if not name.startswith( 'sqlite_' ) }
   assert user_tables
