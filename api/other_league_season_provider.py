from __future__ import annotations

from .database_connection_provider import DatabaseConnectionProvider
from .other_league_skater_season import OtherLeagueSkaterSeason


class OtherLeagueSeasonProvider():
   @classmethod
   def seasons_for_season_id(
         cls,
         season_id: int,
         db_path: str ) -> list[ OtherLeagueSkaterSeason ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.execute(
            '''
            SELECT *
            FROM OtherLeagueSeason
            WHERE SEASON_ID = ?
            ORDER BY PLAYER_ID, LEAGUE
            ''',
            ( season_id, ) )
         return [ OtherLeagueSkaterSeason.from_row( row ) for row in cursor.fetchall() ]
      finally:
         DatabaseConnectionProvider.close( conn )


   @classmethod
   def seasons_for_player_id(
         cls,
         player_id: int,
         db_path: str ) -> list[ OtherLeagueSkaterSeason ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.execute(
            '''
            SELECT *
            FROM OtherLeagueSeason
            WHERE PLAYER_ID = ?
            ORDER BY SEASON_ID, LEAGUE
            ''',
            ( player_id, ) )
         return [ OtherLeagueSkaterSeason.from_row( row ) for row in cursor.fetchall() ]
      finally:
         DatabaseConnectionProvider.close( conn )


   @classmethod
   def seasons_for_player_ids(
         cls,
         player_ids: list[ int ],
         db_path: str ) -> list[ OtherLeagueSkaterSeason ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         placeholders = ', '.join( '?' for _ in player_ids )
         cursor = conn.execute(
            f'''
            SELECT *
            FROM OtherLeagueSeason
            WHERE PLAYER_ID IN ( { placeholders } )
            ORDER BY PLAYER_ID, SEASON_ID, LEAGUE
            ''',
            tuple( player_ids ) )
         return [ OtherLeagueSkaterSeason.from_row( row ) for row in cursor.fetchall() ]
      finally:
         DatabaseConnectionProvider.close( conn )
