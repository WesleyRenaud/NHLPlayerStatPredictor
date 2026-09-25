from __future__ import annotations

import sqlite3

from ...database_connection_provider import DatabaseConnectionProvider
from ..player_name_summary import PlayerNameSummary
from ...seed.schema_creator import SchemaCreator
from ...skaters.skater_position import SkaterPosition
from ...skaters.team import Team


class PlayerNameProvider():
   @classmethod
   def summaries( cls, db_path: str, target_season_id: int ) -> list[ PlayerNameSummary ]:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         SchemaCreator.create( conn.cursor() )
         cursor = conn.execute(
            '''
            SELECT
               roster.PLAYER_ID,
               roster.PLAYER_NAME,
               roster.POSITION,
               roster.TEAM,
               COALESCE( first_season.FIRST_SEASON_ID, ? ) AS FIRST_SEASON_ID
            FROM RosterSkater AS roster
            LEFT JOIN (
               SELECT PLAYER_ID, MIN( SEASON_ID ) AS FIRST_SEASON_ID
               FROM SkaterSeason
               GROUP BY PLAYER_ID
            ) AS first_season
               ON roster.PLAYER_ID = first_season.PLAYER_ID
            WHERE EXISTS (
               SELECT 1
               FROM SkaterSeason AS nhl
               WHERE nhl.PLAYER_ID = roster.PLAYER_ID
            ) OR EXISTS (
               SELECT 1
               FROM OtherLeagueSeason AS other
               WHERE other.PLAYER_ID = roster.PLAYER_ID
            )
            ORDER BY
               roster.PLAYER_NAME,
               FIRST_SEASON_ID,
               roster.PLAYER_ID
            ''',
            ( target_season_id, ) )
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
