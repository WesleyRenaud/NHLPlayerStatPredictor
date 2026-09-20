from __future__ import annotations

import sqlite3

from .database_connection_provider import DatabaseConnectionProvider
from .player_landing_fetcher import PlayerLandingFetcher
from .player_status_builder import PlayerStatusBuilder
from .player_status_store import PlayerStatusStore
from .shared.enums.position import Position


class PlayerStatusHydrator():
   @classmethod
   def hydrate( cls, db_path: str ) -> None:
      player_ids = cls._player_ids( db_path )

      if not player_ids or cls._has_status( db_path ):
         return

      landings = PlayerLandingFetcher.fetch( player_ids, force=False )
      PlayerStatusStore.insert_rows(
         PlayerStatusBuilder.build_all( player_ids, landings ),
         db_path )


   @classmethod
   def _player_ids( cls, db_path: str ) -> list[ int ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.execute(
            '''
            SELECT DISTINCT PLAYER_ID
            FROM SkaterSeason
            ORDER BY PLAYER_ID
            ''' )
         return [ int( row[ Position.FIRST ] ) for row in cursor.fetchall() ]
      except sqlite3.OperationalError:
         return []
      finally:
         DatabaseConnectionProvider.close( conn )


   @classmethod
   def _has_status( cls, db_path: str ) -> bool:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         row = conn.execute( 'SELECT 1 FROM PlayerStatus LIMIT 1' ).fetchone()
         return row is not None
      except sqlite3.OperationalError:
         return False
      finally:
         DatabaseConnectionProvider.close( conn )
