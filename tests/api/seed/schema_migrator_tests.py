from __future__ import annotations

from pathlib import Path
import sqlite3

from api.other_league_season_provider import OtherLeagueSeasonProvider
from api.other_league_season_store import OtherLeagueSeasonStore
from api.other_league_skater_season import OtherLeagueSkaterSeason
from api.seed.schema_creator import SchemaCreator
from api.seed.schema_migrator import SchemaMigrator
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition


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

   SchemaMigrator.migrate( db_path )
   row = _row()
   OtherLeagueSeasonStore.insert_rows( [ row ], db_path=db_path )
   rows = OtherLeagueSeasonProvider.seasons_for_player_id( row.player_id, db_path )
   assert len( rows ) == 1
   assert rows[ Position.FIRST ] == row


def Test_Migrate_TestCurrentSchema_ExpectIdempotent( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   conn = sqlite3.connect( db_path )

   try:
      SchemaCreator.create( conn.cursor() )
      conn.commit()
   finally:
      conn.close()

   SchemaMigrator.migrate( db_path )
   SchemaMigrator.migrate( db_path )
   row = _row()
   OtherLeagueSeasonStore.insert_rows( [ row ], db_path=db_path )
   rows = OtherLeagueSeasonProvider.seasons_for_player_id( row.player_id, db_path )
   assert len( rows ) == 1
   assert rows[ Position.FIRST ] == row
