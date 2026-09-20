from __future__ import annotations

from ..seed_sql_loader import SeedSqlLoader
from ...types import Types


class OtherLeagueSeasonSeedTable():
   SQL_FILE = 'other_league_season.sql'


   @classmethod
   def create_table( cls, cursor: Types.Cursor ) -> None:
      SeedSqlLoader.execute_sql_file( cursor, SeedSqlLoader.seed_sql_path( cls.SQL_FILE ) )
