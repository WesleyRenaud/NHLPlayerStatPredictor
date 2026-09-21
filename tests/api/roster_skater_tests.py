from __future__ import annotations

from api.roster_skater import RosterSkater
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def Test_FromRow_TestStoredFields_ExpectValues() -> None:
   position = list( SkaterPosition )[ Position.FIRST ]
   team = list( Team )[ Position.FIRST ]
   row = RosterSkater.from_row( {
      'PLAYER_ID': 7,
      'PLAYER_NAME': 'Stub Skater',
      'POSITION': position.value,
      'TEAM': team.value,
   } )
   assert row == RosterSkater( 7, 'Stub Skater', position, team )
