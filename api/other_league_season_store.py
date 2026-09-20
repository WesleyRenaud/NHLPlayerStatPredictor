from __future__ import annotations

from dataclasses import asdict

from .database_connection_provider import DatabaseConnectionProvider
from .other_league_season import OtherLeagueSeason
from .seed.schema_creator import SchemaCreator


class OtherLeagueSeasonStore():
   @classmethod
   def insert_rows(
         cls,
         rows: list[ OtherLeagueSeason ],
         db_path: str ) -> None:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.cursor()
         SchemaCreator.create( cursor )
         cursor.execute( 'DELETE FROM OtherLeagueSeason' )

         if rows:
            cursor.executemany(
               '''
               INSERT INTO OtherLeagueSeason (
                  PLAYER_ID, SEASON_ID, LEAGUE, AGE, GAMES_PLAYED, GOALS, ASSISTS,
                  POINTS, G_PACE, A_PACE
               ) VALUES (
                  :player_id, :season_id, :league, :age, :games_played, :goals, :assists,
                  :points, :g_pace, :a_pace
               )
               ''',
               [ asdict( row ) for row in rows ] )

         conn.commit()
      finally:
         DatabaseConnectionProvider.close( conn )
