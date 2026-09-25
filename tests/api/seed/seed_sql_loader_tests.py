from __future__ import annotations

from api.seed.seed_sql_loader import SeedSqlLoader


def Test_SeedSqlPath_TestFileName_ExpectSqlDirectory() -> None:
   file_name = 'stub.sql'

   path = SeedSqlLoader.seed_sql_path( file_name )

   assert path == SeedSqlLoader.SEED_SQL_DIR / file_name
