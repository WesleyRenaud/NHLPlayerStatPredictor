from __future__ import annotations

from dataclasses import asdict

from ..database_connection_provider import DatabaseConnectionProvider
from .nhl_skater_season import NhlSkaterSeason
from ..seed.schema_creator import SchemaCreator


class SkaterSeasonStore():
   @classmethod
   def insert_rows(
         cls,
         rows: list[ NhlSkaterSeason ],
         db_path: str ) -> None:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.cursor()
         SchemaCreator.create( cursor )
         cursor.execute( 'DELETE FROM SkaterSeason' )

         if rows:
            cursor.executemany(
               '''
               INSERT INTO SkaterSeason (
                  PLAYER_ID, SEASON_ID, PLAYER_NAME, POSITION, BIRTH_DATE, AGE, TEAM,
                  GAMES_PLAYED, GOALS, ASSISTS, POINTS, SCHEDULE_GAMES, PACE_GAMES,
                  G_PACE, A_PACE, P_PACE, GP_SHARE
               ) VALUES (
                  :player_id, :season_id, :player_name, :position, :birth_date, :age, :team,
                  :games_played, :goals, :assists, :points, :schedule_games, :pace_games,
                  :g_pace, :a_pace, :p_pace, :gp_share
               )
               ''',
               [ asdict( row ) for row in rows ] )

         conn.commit()
      finally:
         DatabaseConnectionProvider.close( conn )
