from __future__ import annotations

from pathlib import Path

from api.shared.enums.position import Position
from api.skaters.roster_skater import RosterSkater
from api.skaters.roster_skater_provider import RosterSkaterProvider
from api.skaters.roster_skater_store import RosterSkaterStore
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


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

   skaters = RosterSkaterProvider.skaters( db_path )

   assert skaters == [ first, second ]


def Test_Team_TestInsertedPlayer_ExpectTeam( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   first = RosterSkater(
      player_id=1,
      player_name='First Skater',
      position=list( SkaterPosition )[ Position.FIRST ],
      team=list( Team )[ Position.FIRST ] )
   RosterSkaterStore.insert_rows( [ first ], db_path=db_path )

   team = RosterSkaterProvider.team( first.player_id, db_path )

   assert team == first.team


def Test_Team_TestMissingPlayer_ExpectNone( tmp_path: Path ) -> None:
   db_path = str( tmp_path / 'skaters.sqlite' )
   player_id = 1
   RosterSkaterStore.insert_rows( [], db_path=db_path )

   team = RosterSkaterProvider.team( player_id, db_path )

   assert team is None
