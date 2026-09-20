from __future__ import annotations

from dataclasses import asdict

from .database_connection_provider import DatabaseConnectionProvider
from .roster_skater import RosterSkater
from .seed.schema_creator import SchemaCreator


class RosterSkaterStore():
   @classmethod
   def insert_rows(
         cls,
         rows: list[ RosterSkater ],
         db_path: str ) -> None:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.cursor()
         SchemaCreator.create( cursor )
         cursor.execute( 'DELETE FROM RosterSkater' )

         if rows:
            cursor.executemany(
               '''
               INSERT INTO RosterSkater (
                  PLAYER_ID, PLAYER_NAME, POSITION, TEAM
               ) VALUES (
                  :player_id, :player_name, :position, :team
               )
               ''',
               [ asdict( row ) for row in rows ] )

         conn.commit()
      finally:
         DatabaseConnectionProvider.close( conn )
