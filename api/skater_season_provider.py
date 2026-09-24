from __future__ import annotations

from .database_connection_provider import DatabaseConnectionProvider
from .nhl_skater_season import NhlSkaterSeason


class SkaterSeasonProvider():
   @classmethod
   def seasons_for_name(
         cls,
         player_name: str,
         db_path: str ) -> list[ NhlSkaterSeason ]:
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
         return [ NhlSkaterSeason.from_row( row ) for row in cursor.fetchall() ]
      finally:
         DatabaseConnectionProvider.close( conn )


   @classmethod
   def seasons_for_season_id(
         cls,
         season_id: int,
         db_path: str ) -> list[ NhlSkaterSeason ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.execute(
            '''
            SELECT *
            FROM SkaterSeason
            WHERE SEASON_ID = ?
            ORDER BY PLAYER_ID
            ''',
            ( season_id, ) )
         return [ NhlSkaterSeason.from_row( row ) for row in cursor.fetchall() ]
      finally:
         DatabaseConnectionProvider.close( conn )


   @classmethod
   def seasons_for_player_id(
         cls,
         player_id: int,
         db_path: str ) -> list[ NhlSkaterSeason ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.execute(
            '''
            SELECT *
            FROM SkaterSeason
            WHERE PLAYER_ID = ?
            ORDER BY SEASON_ID
            ''',
            ( player_id, ) )
         return [ NhlSkaterSeason.from_row( row ) for row in cursor.fetchall() ]
      finally:
         DatabaseConnectionProvider.close( conn )


   @classmethod
   def seasons_for_player_ids(
         cls,
         player_ids: list[ int ],
         db_path: str ) -> list[ NhlSkaterSeason ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         placeholders = ', '.join( '?' for _ in player_ids )
         cursor = conn.execute(
            f'''
            SELECT *
            FROM SkaterSeason
            WHERE PLAYER_ID IN ( { placeholders } )
            ORDER BY PLAYER_ID, SEASON_ID
            ''',
            tuple( player_ids ) )
         return [ NhlSkaterSeason.from_row( row ) for row in cursor.fetchall() ]
      finally:
         DatabaseConnectionProvider.close( conn )
