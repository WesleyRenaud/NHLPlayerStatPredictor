from __future__ import annotations

import sqlite3

from ...database_connection_provider import DatabaseConnectionProvider
from ..player_name_summary import PlayerNameSummary
from ...skater_position import SkaterPosition
from ...team import Team


class PlayerNameProvider():
   @classmethod
   def summaries( cls, db_path: str ) -> list[ PlayerNameSummary ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.execute(
            '''
            SELECT
               latest.PLAYER_ID,
               latest.PLAYER_NAME,
               latest.POSITION,
               latest.TEAM,
               first_season.FIRST_SEASON_ID
            FROM SkaterSeason AS latest
            INNER JOIN (
               SELECT PLAYER_ID, MAX( SEASON_ID ) AS SEASON_ID
               FROM SkaterSeason
               GROUP BY PLAYER_ID
            ) AS latest_season
               ON latest.PLAYER_ID = latest_season.PLAYER_ID
               AND latest.SEASON_ID = latest_season.SEASON_ID
            INNER JOIN (
               SELECT PLAYER_ID, MIN( SEASON_ID ) AS FIRST_SEASON_ID
               FROM SkaterSeason
               GROUP BY PLAYER_ID
            ) AS first_season
               ON latest.PLAYER_ID = first_season.PLAYER_ID
            INNER JOIN (
               SELECT MAX( SEASON_ID ) AS SEASON_ID
               FROM SkaterSeason
            ) AS current_season
               ON latest.SEASON_ID = current_season.SEASON_ID
            ORDER BY
               latest.PLAYER_NAME,
               first_season.FIRST_SEASON_ID,
               latest.PLAYER_ID
            ''' )
         return [
            PlayerNameSummary(
               player_id=int( row[ 'PLAYER_ID' ] ),
               player_name=str( row[ 'PLAYER_NAME' ] ),
               position=SkaterPosition( str( row[ 'POSITION' ] ) ),
               team=Team( str( row[ 'TEAM' ] ) ),
               first_season_id=int( row[ 'FIRST_SEASON_ID' ] ) )
            for row in cursor.fetchall()
         ]
      except sqlite3.OperationalError:
         return []
      finally:
         DatabaseConnectionProvider.close( conn )
