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


def Test_Bind_TestLastToi_ExpectAvailabilityTimesChosen() -> None:
   injury = 0.8
   chosen = 0.5
   low_toi = 16.0
   high_toi = 24.0
   low = _skater( 2, low_toi, 24.0, injury )
   high = _skater( 1, high_toi, 16.0, injury )
   shares = [
      IceChosenShare( low_toi, SkaterGroup( 'D' ), chosen, chosen ),
      IceChosenShare( high_toi, SkaterGroup( 'D' ), GamesShare.FULL, GamesShare.FULL ),
   ]

   bound = ChosenShareBinder.bind( [ low, high ], shares, DepthGroup.defense() )

   by_id = { skater.player_id: skater.availability for skater in bound }
   assert by_id[ high.player_id ] == injury
   assert by_id[ low.player_id ] == injury * chosen
   assert [ skater.player_id for skater in bound ] == [ low.player_id, high.player_id ]


def Test_Bind_TestMidToi_ExpectInterpolatedChosen() -> None:
   injury = 0.8
   low = 0.5
   high = GamesShare.FULL
   last_toi = 20.0
   shares = [
      IceChosenShare( 16.0, SkaterGroup( 'D' ), low, low ),
      IceChosenShare( 24.0, SkaterGroup( 'D' ), high, high ),
   ]

   bound = ChosenShareBinder.bind(
      [ _skater( 1, last_toi, last_toi, injury ) ],
      shares,
      DepthGroup.defense() )

   assert abs(
      bound[ Position.FIRST ].availability
      - injury * ( low + high ) / 2 ) < 0.001


def Test_Bind_TestMissingLastToi_ExpectLowestChosen() -> None:
   injury = 0.8
   chosen = 0.5
   shares = [
      IceChosenShare( 16.0, SkaterGroup( 'D' ), chosen, chosen ),
      IceChosenShare( 24.0, SkaterGroup( 'D' ), GamesShare.FULL, GamesShare.FULL ),
   ]

   bound = ChosenShareBinder.bind(
      [ _skater( 1, None, 0.0, injury ) ],
      shares,
      DepthGroup.defense() )

   assert bound[ Position.FIRST ].availability == injury * chosen
