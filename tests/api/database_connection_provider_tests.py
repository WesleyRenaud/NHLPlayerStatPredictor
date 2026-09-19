from __future__ import annotations

from pathlib import Path

from api.database_connection_provider import DatabaseConnectionProvider
from api.position import Position


def Test_Open_TestNewPath_ExpectQueryableConnection( tmp_path: Path ) -> None:
   conn = DatabaseConnectionProvider.open( str( tmp_path / 'skaters.sqlite' ) )

   try:
      value = conn.execute( 'SELECT 1' ).fetchone()[ Position.FIRST ]
   finally:
      DatabaseConnectionProvider.close( conn )

   assert value == 1
