from __future__ import annotations

from api.chosen_share_binder import ChosenShareBinder
from api.depth_group import DepthGroup
from api.games_share import GamesShare
from api.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skater_group import SkaterGroup
from api.skater_position import SkaterPosition
from api.slot_chosen_share import SlotChosenShare
from api.team import Team


def _skater( player_id: int, implied: float, availability: float ) -> IceSkater:
   return IceSkater(
      player_id,
      str( player_id ),
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      implied,
      implied,
      availability )


def Test_Bind_TestRankedSlots_ExpectAvailabilityTimesChosen() -> None:
   group = DepthGroup.defense()
   bound = ChosenShareBinder.bind(
      [ _skater( 2, 16.0, 0.8 ), _skater( 1, 24.0, 0.8 ) ],
      [
         SlotChosenShare( 1, SkaterGroup( 'D' ), GamesShare.FULL, GamesShare.FULL ),
         SlotChosenShare( 2, SkaterGroup( 'D' ), 0.5, 0.5 ),
      ],
      group )
   by_id = { skater.player_id: skater.availability for skater in bound }
   assert by_id[ 1 ] == 0.8
   assert by_id[ 2 ] == 0.4
   assert [ skater.player_id for skater in bound ] == [ 2, 1 ]
