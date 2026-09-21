from __future__ import annotations

from pathlib import Path

from api.roster_skater import RosterSkater
from api.roster_skater_provider import RosterSkaterProvider
from api.roster_skater_store import RosterSkaterStore
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def Test_Skaters_TestInsertedRows_ExpectAll( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   first = RosterSkater(
      player_id=1,
      player_name='First Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      team=list( Team )[ Position.FIRST ] )
   second = RosterSkater(
      player_id=2,
      player_name='Second Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      team=list( Team )[ Position.SECOND ] )
   RosterSkaterStore.insert_rows( [ first, second ], db_path=db_path )
   assert RosterSkaterProvider.skaters( db_path ) == [ first, second ]
