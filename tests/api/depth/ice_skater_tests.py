from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_Fields_TestSkater_ExpectValues() -> None:
   player_id = 7
   player_name = 'Brock Faber'
   position = SkaterPosition( 'D' )
   implied = 24.1
   last_toi = 24.68
   availability = GamesShare.FULL
   skater = IceSkater(
      player_id,
      player_name,
      position,
      list( Team )[ Position.FIRST ],
      implied,
      last_toi,
      availability )

   assert skater.player_id == player_id
   assert skater.player_name == player_name
   assert skater.position == position
   assert skater.implied == implied
   assert skater.last_toi == last_toi
   assert skater.availability == availability
