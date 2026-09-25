from __future__ import annotations

from pathlib import Path

from api.database_connection_provider import DatabaseConnectionProvider
from api.shared.enums.position import Position


def Test_Open_TestNewPath_ExpectQueryableConnection( tmp_path: Path ) -> None:
   expected = 1
   conn = DatabaseConnectionProvider.open( str( tmp_path / 'skaters.sqlite' ) )

   try:
      value = conn.execute( f'SELECT { expected }' ).fetchone()[ Position.FIRST ]
   finally:
      DatabaseConnectionProvider.close( conn )

   assert value == expected
