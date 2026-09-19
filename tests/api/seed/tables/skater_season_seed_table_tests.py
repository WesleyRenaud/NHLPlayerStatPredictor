from __future__ import annotations

from pathlib import Path
import sqlite3

from api.position import Position
from api.seed.tables.skater_season_seed_table import SkaterSeasonSeedTable


def Test_CreateTable_TestNewDatabase_ExpectSkaterSeasonsTable( tmp_path: Path ) -> None:
   conn = sqlite3.connect( str( tmp_path / 'skaters.sqlite' ) )

   try:
      SkaterSeasonSeedTable.create_table( conn.cursor() )
      names = {
         row[ Position.FIRST ]
         for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'" )
      }
   finally:
      conn.close()

   assert 'SkaterSeason' in names
