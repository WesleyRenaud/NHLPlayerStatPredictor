from __future__ import annotations

from api.ice_usage import IceUsage
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def Test_Fields_TestUsage_ExpectValues() -> None:
   team = list( Team )[ Position.FIRST ]
   usage = IceUsage( 24.68, 80, team, SkaterPosition( 'D' ) )
   assert usage.toi == 24.68
   assert usage.games == 80
   assert usage.team == team
   assert usage.position == SkaterPosition( 'D' )
