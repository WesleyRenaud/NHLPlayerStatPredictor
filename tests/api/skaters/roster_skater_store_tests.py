from __future__ import annotations

from pathlib import Path

from api.database_connection_provider import DatabaseConnectionProvider
from api.shared.enums.position import Position
from api.skaters.roster_skater import RosterSkater
from api.skaters.roster_skater_store import RosterSkaterStore
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_InsertRows_TestInsertedSkater_ExpectPersistedName( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   row = RosterSkater(
      player_id=7,
      player_name='Stub Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      team=list( Team )[ Position.FIRST ] )
   RosterSkaterStore.insert_rows( [ row ], db_path=db_path )
   conn = DatabaseConnectionProvider.open( db_path )

   try:
      stored = conn.execute(
         'SELECT PLAYER_NAME FROM RosterSkater WHERE PLAYER_ID = ?',
         ( row.player_id, ) ).fetchone()
   finally:
      DatabaseConnectionProvider.close( conn )

   assert stored[ Position.FIRST ] == row.player_name
