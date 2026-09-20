from __future__ import annotations

from pathlib import Path

from api.database_connection_provider import DatabaseConnectionProvider
from api.player_status import PlayerStatus
from api.player_status_store import PlayerStatusStore
from api.shared.enums.position import Position


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

   assert stored[ Position.FIRST ]
