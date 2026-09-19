from __future__ import annotations

import sqlite3

from ...database_connection_provider import DatabaseConnectionProvider
from ...position import Position


class PlayerNameProvider():
   @classmethod
   def names( cls, db_path: str ) -> list[ str ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.execute(
            '''
            SELECT DISTINCT PLAYER_NAME
            FROM SkaterSeason
            ORDER BY PLAYER_NAME
            ''' )
         return [ str( row[ Position.FIRST ] ) for row in cursor.fetchall() ]
      except sqlite3.OperationalError:
         return []
      finally:
         DatabaseConnectionProvider.close( conn )
