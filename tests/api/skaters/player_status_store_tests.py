from __future__ import annotations

from pathlib import Path

from api.database_connection_provider import DatabaseConnectionProvider
from api.shared.enums.position import Position
from api.skaters.player_status import PlayerStatus
from api.skaters.player_status_store import PlayerStatusStore


def Test_InsertRows_TestInsertedStatus_ExpectPersistedFlag( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   row = PlayerStatus( player_id=7, is_active=True )
   PlayerStatusStore.insert_rows( [ row ], db_path=db_path )
   conn = DatabaseConnectionProvider.open( db_path )

   try:
      stored = conn.execute(
         'SELECT IS_ACTIVE FROM PlayerStatus WHERE PLAYER_ID = ?',
         ( row.player_id, ) ).fetchone()
   finally:
      DatabaseConnectionProvider.close( conn )

   assert stored[ Position.FIRST ] == row.is_active


def Test_Read_TestInsertedRows_ExpectAll( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   row = PlayerStatus( player_id=7, is_active=False )
   PlayerStatusStore.insert_rows( [ row ], db_path=db_path )

   loaded = PlayerStatusStore.read( db_path )

   assert loaded == [ row ]
