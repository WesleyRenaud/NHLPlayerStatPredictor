from __future__ import annotations

from .database_connection_provider import DatabaseConnectionProvider
from .roster_skater import RosterSkater


class RosterSkaterProvider():
   @classmethod
   def skaters( cls, db_path: str ) -> list[ RosterSkater ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.execute(
            '''
            SELECT *
            FROM RosterSkater
            ORDER BY PLAYER_ID
            ''' )
         return [ RosterSkater.from_row( row ) for row in cursor.fetchall() ]
      finally:
         DatabaseConnectionProvider.close( conn )
