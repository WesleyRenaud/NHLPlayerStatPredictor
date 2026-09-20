from __future__ import annotations

from .database_connection_provider import DatabaseConnectionProvider
from .other_league_season import OtherLeagueSeason


class OtherLeagueSeasonProvider():
   @classmethod
   def seasons_for_player_id(
         cls,
         player_id: int,
         db_path: str ) -> list[ OtherLeagueSeason ]:
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
         return [ OtherLeagueSeason.from_row( row ) for row in cursor.fetchall() ]
      finally:
         DatabaseConnectionProvider.close( conn )
