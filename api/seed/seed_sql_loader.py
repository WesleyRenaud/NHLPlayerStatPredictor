from __future__ import annotations

from pathlib import Path

from ..types import Types


class SeedSqlLoader():
   SEED_SQL_DIR = Path( __file__ ).parent / 'sql'


   @classmethod
   def seed_sql_path( cls, filename: str ) -> Path:
      return cls.SEED_SQL_DIR / filename


   @classmethod
   def execute_sql_file( cls, cursor: Types.Cursor, path: Path ) -> None:
      cursor.executescript( path.read_text( encoding='utf-8' ) )
