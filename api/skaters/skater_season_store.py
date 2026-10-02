from __future__ import annotations

from dataclasses import asdict

from ..database_connection_provider import DatabaseConnectionProvider
from .nhl_skater_season import NhlSkaterSeason
from ..seed.schema_migrator import SchemaMigrator


class SkaterSeasonStore():
   @classmethod
   def insert_rows(
         cls,
         rows: list[ NhlSkaterSeason ],
         db_path: str ) -> None:
      conn = DatabaseConnectionProvider.open( db_path )

      try:
         cursor = conn.cursor()
         SchemaMigrator.apply( cursor )
         cursor.execute( 'DELETE FROM SkaterSeason' )

         if rows:
            cursor.executemany(
               '''
               INSERT INTO SkaterSeason (
                  PLAYER_ID, SEASON_ID, PLAYER_NAME, POSITION, BIRTH_DATE, AGE, TEAM,
                  GAMES_PLAYED, GOALS, ASSISTS, POINTS, PIM, SCHEDULE_GAMES, PACE_GAMES,
                  G_PACE, A_PACE, P_PACE, GP_SHARE, PLAYOFF_GAMES, PLAYOFF_GOALS, PLAYOFF_ASSISTS,
                  PP_GOALS, PP_POINTS, SHORT_HANDED_GOALS, SHORT_HANDED_POINTS, EV_GOALS, EV_POINTS, SHOTS
               ) VALUES (
                  :player_id, :season_id, :player_name, :position, :birth_date, :age, :team,
                  :games_played, :goals, :assists, :points, :penalty_minutes, :schedule_games, :pace_games,
                  :g_pace, :a_pace, :p_pace, :gp_share, :playoff_games, :playoff_goals, :playoff_assists,
                  :power_play_goals, :power_play_points, :short_handed_goals, :short_handed_points,
                  :even_strength_goals, :even_strength_points, :shots
               )
               ''',
               [ asdict( row ) for row in rows ] )

         conn.commit()
      finally:
         DatabaseConnectionProvider.close( conn )
