from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.chosen_share_binder import ChosenShareBinder
from api.depth.depth_group import DepthGroup
from api.depth.ice_chosen_share import IceChosenShare
from api.depth.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skaters.skater_group import SkaterGroup
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _skater(
      player_id: int,
      last_toi: float | None,
      implied: float,
      availability: float ) -> IceSkater:
   return IceSkater(
      player_id,
      str( player_id ),
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      implied,
      last_toi,
      availability )


def _shares() -> list[ IceChosenShare ]:
   group = SkaterGroup( 'D' )
   return [
      IceChosenShare( 16.0, group, 0.5, 0.5 ),
      IceChosenShare( 24.0, group, GamesShare.FULL, GamesShare.FULL ),
   ]


def Test_Bind_TestLastToi_ExpectAvailabilityTimesChosen() -> None:
   bound = ChosenShareBinder.bind(
      [ _skater( 2, 16.0, 24.0, 0.8 ), _skater( 1, 24.0, 16.0, 0.8 ) ],
      _shares(),
      DepthGroup.defense() )
   by_id = { skater.player_id: skater.availability for skater in bound }
   assert by_id[ 1 ] == 0.8
   assert by_id[ 2 ] == 0.4
   assert [ skater.player_id for skater in bound ] == [ 2, 1 ]


def Test_Bind_TestMidToi_ExpectInterpolatedChosen() -> None:
   bound = ChosenShareBinder.bind(
      [ _skater( 1, 20.0, 20.0, 0.8 ) ],
      _shares(),
      DepthGroup.defense() )
   assert abs( bound[ Position.FIRST ].availability - 0.6 ) < 0.001


def Test_Bind_TestMissingLastToi_ExpectLowestChosen() -> None:
   bound = ChosenShareBinder.bind(
      [ _skater( 1, None, 0.0, 0.8 ) ],
      _shares(),
      DepthGroup.defense() )
   assert bound[ Position.FIRST ].availability == 0.4
