from __future__ import annotations

from api.depth.ice_usage import IceUsage
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_Fields_TestUsage_ExpectValues() -> None:
   toi = 24.68
   games = 80
   team = list( Team )[ Position.FIRST ]
   position = SkaterPosition( 'D' )
   usage = IceUsage( toi, games, team, position )

   assert usage.toi == toi
   assert usage.games == games
   assert usage.team == team
   assert usage.position == position
