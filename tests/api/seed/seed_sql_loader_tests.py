from __future__ import annotations

from api.seed.seed_sql_loader import SeedSqlLoader


def Test_SeedSqlPath_TestFileName_ExpectSqlDirectory() -> None:
   path = SeedSqlLoader.seed_sql_path( 'stub.sql' )
   assert path == SeedSqlLoader.SEED_SQL_DIR / 'stub.sql'
