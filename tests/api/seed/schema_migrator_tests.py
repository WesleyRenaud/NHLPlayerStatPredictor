from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3

from api.seed.schema_creator import SchemaCreator
from api.seed.schema_migrator import SchemaMigrator
from api.skaters.other_league_season_provider import OtherLeagueSeasonProvider
from api.skaters.other_league_season_store import OtherLeagueSeasonStore
from api.skaters.other_league_skater_season import OtherLeagueSkaterSeason
from api.skaters.skater_position import SkaterPosition


def _row() -> OtherLeagueSkaterSeason:
   return OtherLeagueSkaterSeason(
      player_id=7,
      season_id=20252026,
      league='AAA',
      position=SkaterPosition( 'C' ),
      age=20.8,
      games_played=46,
      goals=6,
      assists=13,
      points=19,
      g_pace=10.0,
      a_pace=20.0 )


def Test_Migrate_TestPriorSchema_ExpectReadableByPlayer( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   conn = sqlite3.connect( db_path )

   try:
      conn.execute(
         '''
         CREATE TABLE OtherLeagueSeason
         (  PLAYER_ID    INTEGER NOT NULL,
            SEASON_ID    INTEGER NOT NULL,
            LEAGUE       TEXT    NOT NULL,
            AGE          REAL    NOT NULL,
            GAMES_PLAYED INTEGER,
            GOALS        INTEGER,
            ASSISTS      INTEGER,
            POINTS       INTEGER,
            G_PACE       REAL,
            A_PACE       REAL,
            PRIMARY KEY ( PLAYER_ID, SEASON_ID, LEAGUE ) )
         ''' )
      conn.commit()
   finally:
      conn.close()

   row = _row()
   SchemaMigrator.migrate( db_path )
   OtherLeagueSeasonStore.insert_rows( [ row ], db_path=db_path )

   rows = OtherLeagueSeasonProvider.seasons_for_player_id( row.player_id, db_path )

   assert rows == [ row ]


def Test_Migrate_TestPriorSkaterSeasonSchema_ExpectZeroPlayoffTotals( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )

   with closing( sqlite3.connect( db_path ) ) as conn:
      conn.execute(
         '''
         CREATE TABLE SkaterSeason
         (  PLAYER_ID      INTEGER NOT NULL,
            SEASON_ID      INTEGER NOT NULL,
            PLAYER_NAME    TEXT    NOT NULL,
            POSITION       TEXT,
            BIRTH_DATE     DATE    NOT NULL,
            AGE            REAL    NOT NULL,
            TEAM           TEXT,
            GAMES_PLAYED   INTEGER,
            GOALS          INTEGER,
            ASSISTS        INTEGER,
            POINTS         INTEGER,
            SCHEDULE_GAMES INTEGER,
            PACE_GAMES     INTEGER,
            G_PACE         REAL,
            A_PACE         REAL,
            P_PACE         REAL,
            GP_SHARE       REAL,
            PRIMARY KEY ( PLAYER_ID, SEASON_ID ) )
         ''' )
      conn.execute(
         '''
         INSERT INTO SkaterSeason ( PLAYER_ID, SEASON_ID, PLAYER_NAME, BIRTH_DATE, AGE )
         VALUES ( 7, 20252026, 'Stub Skater', '1997-01-13', 28.7 )
         ''' )
      conn.commit()

   SchemaMigrator.migrate( db_path )

   with closing( sqlite3.connect( db_path ) ) as conn:
      totals = conn.execute(
         'SELECT PLAYOFF_GAMES, PLAYOFF_GOALS, PLAYOFF_ASSISTS FROM SkaterSeason' ).fetchall()
      short_handed = conn.execute(
         'SELECT SHORT_HANDED_GOALS, SHORT_HANDED_POINTS FROM SkaterSeason' ).fetchall()

   assert totals == [ ( 0, 0, 0 ) ]
   assert short_handed == [ ( None, None ) ]


def Test_Migrate_TestCurrentSchema_ExpectIdempotent( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   conn = sqlite3.connect( db_path )

   try:
      SchemaCreator.create( conn.cursor() )
      conn.commit()
   finally:
      conn.close()

   row = _row()
   SchemaMigrator.migrate( db_path )
   SchemaMigrator.migrate( db_path )
   OtherLeagueSeasonStore.insert_rows( [ row ], db_path=db_path )

   rows = OtherLeagueSeasonProvider.seasons_for_player_id( row.player_id, db_path )

   assert rows == [ row ]
