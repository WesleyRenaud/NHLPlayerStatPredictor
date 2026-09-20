from __future__ import annotations

from dataclasses import asdict

from .database_connection_provider import DatabaseConnectionProvider
from .player_status import PlayerStatus
from .seed.schema_creator import SchemaCreator


class PlayerStatusStore():
   @classmethod
   def insert_rows(
         cls,
         rows: list[ PlayerStatus ],
         db_path: str ) -> None:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.cursor()
         SchemaCreator.create( cursor )
         cursor.execute( 'DELETE FROM PlayerStatus' )

         if rows:
            cursor.executemany(
               '''
               INSERT INTO PlayerStatus (
                  PLAYER_ID, IS_ACTIVE
               ) VALUES (
                  :player_id, :is_active
               )
               ''',
               [ asdict( row ) for row in rows ] )

         conn.commit()
      finally:
         DatabaseConnectionProvider.close( conn )
