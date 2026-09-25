from __future__ import annotations

from api.depth.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_Fields_TestSkater_ExpectValues() -> None:
   skater = IceSkater(
      7,
      'Brock Faber',
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      24.1,
      24.68,
      1.0 )
   assert skater.player_id == 7
   assert skater.player_name == 'Brock Faber'
   assert skater.position == SkaterPosition( 'D' )
   assert skater.implied == 24.1
   assert skater.last_toi == 24.68
   assert skater.availability == 1.0
