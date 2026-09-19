from __future__ import annotations

from .database_connection_provider import DatabaseConnectionProvider
from .skater_season import SkaterSeason


class SkaterSeasonProvider():
   @classmethod
   def seasons_for_name(
         cls,
         player_name: str,
         db_path: str ) -> list[ SkaterSeason ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.execute(
            '''
            SELECT *
            FROM SkaterSeason
            WHERE lower( PLAYER_NAME ) LIKE ?
            ORDER BY PLAYER_NAME, SEASON_ID
            ''',
            ( f'%{ player_name.strip().lower() }%', ) )
         return [ SkaterSeason.from_row( row ) for row in cursor.fetchall() ]
      finally:
         DatabaseConnectionProvider.close( conn )
