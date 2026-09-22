from __future__ import annotations

from pathlib import Path
import sqlite3

from ..database_connection_provider import DatabaseConnectionProvider
from .schema_creator import SchemaCreator
from .seed_sql_loader import SeedSqlLoader
from ..types import Types


class SchemaMigrator():
   MIGRATIONS_DIR = Path( __file__ ).resolve().parent / 'migrations'


   @classmethod
   def migrate( cls, db_path: str ) -> None:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.cursor()
         cls.apply( cursor )
         conn.commit()
      finally:
         DatabaseConnectionProvider.close( conn )


   @classmethod
   def apply( cls, cursor: Types.Cursor ) -> None:
      SchemaCreator.create( cursor )
      cursor.execute(
         '''
         CREATE TABLE IF NOT EXISTS SchemaMigration
         (  VERSION TEXT NOT NULL PRIMARY KEY )
         ''' )
      applied = {
         row[ 0 ]
         for row in cursor.execute( 'SELECT VERSION FROM SchemaMigration' )
      }

      for path in sorted( SchemaMigrator.MIGRATIONS_DIR.glob( '*.sql' ) ):
         version = path.stem

         if version in applied:
            continue

         try:
            SeedSqlLoader.execute_sql_file( cursor, path )
         except sqlite3.OperationalError as error:
            if 'duplicate column name' not in str( error ).lower():
               raise

         cursor.execute(
            'INSERT INTO SchemaMigration ( VERSION ) VALUES ( ? )',
            ( version, ) )
         print( f'Applied { version }', flush=True )
