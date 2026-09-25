from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_group import DepthGroup
from api.depth.ice_allocator import IceAllocator
from api.depth.ice_skater import IceSkater
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _skater(
      player_id: int,
      implied: float,
      availability: float = GamesShare.FULL ) -> IceSkater:
   return IceSkater(
      player_id,
      str( player_id ),
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      implied,
      implied,
      availability )


def _toi(
      projected: list[ tuple[ IceSkater, float ] ],
      player_id: int ) -> float:
   return next(
      toi
      for skater, toi in projected
      if skater.player_id == player_id )


def _six( availability: float = GamesShare.FULL ) -> list[ IceSkater ]:
   return [ _skater( index, 20.0, availability ) for index in range( 1, 7 ) ]


def _project(
      regulars: list[ IceSkater ],
      extras: list[ IceSkater ] ) -> list[ tuple[ IceSkater, float ] ]:
   return IceAllocator.project(
      regulars,
      extras,
      [],
      DepthGroup.defense() )


def Test_Project_TestSixClaims_ExpectPieAndRatios() -> None:
   projected = _project(
      [
         _skater( 1, 26.0 ),
         _skater( 2, 24.0 ),
         _skater( 3, 20.0 ),
         _skater( 4, 20.0 ),
         _skater( 5, 16.0 ),
         _skater( 6, 14.0 ),
      ],
      [ _skater( 7, 12.0 ) ] )
   total = sum( toi for _skater_row, toi in projected )
   assert abs( total - DepthGroup.DEFENSE_ICE_MINUTES ) < 0.001
   assert abs( _toi( projected, 1 ) / _toi( projected, 2 ) - 26.0 / 24.0 ) < 0.001


def Test_Project_TestInjuredTeammate_ExpectHealthyGetsMore() -> None:
   even = _project( _six(), [] )
   boosted = _project(
      [ _skater( 1, 20.0 ), _skater( 2, 20.0, 0.5 ), *_six()[ 2: ] ],
      [] )
   assert _toi( boosted, 1 ) > _toi( even, 1 )


def Test_Project_TestExtraFillsInjuredSlot_ExpectLessBoost() -> None:
   injured = [
      _skater( 1, 20.0 ),
      _skater( 2, 20.0, 0.5 ),
      *_six()[ 2: ],
   ]
   without = _project( injured, [] )
   with_extra = _project( injured, [ _skater( 7, 16.0 ) ] )
   assert _toi( with_extra, 1 ) < _toi( without, 1 )


def Test_Project_TestNoNamedExtra_ExpectHealthyGetsMore() -> None:
   even = _project( _six(), [] )
   missing = _project(
      [ _skater( 1, 20.0 ), _skater( 2, 20.0, 0.5 ), *_six()[ 2: ] ],
      [] )
   assert _toi( missing, 1 ) > _toi( even, 1 )


def Test_Project_TestTwoAlwaysOut_ExpectMoreThanOneOut() -> None:
   one_out = _project(
      [
         _skater( 1, 20.0 ),
         _skater( 2, 20.0, 0.0 ),
         *_six()[ 2: ],
      ],
      [] )
   two_out = _project(
      [
         _skater( 1, 20.0 ),
         _skater( 2, 20.0, 0.0 ),
         _skater( 3, 20.0 ),
         _skater( 4, 20.0, 0.0 ),
         *_six()[ 4: ],
      ],
      [] )
   assert _toi( two_out, 1 ) > _toi( one_out, 1 )


def Test_Project_TestTwoHalfOut_ExpectOverlapBoost() -> None:
   one_half = _project(
      [
         _skater( 1, 20.0 ),
         _skater( 2, 20.0, 0.5 ),
         *_six()[ 2: ],
      ],
      [] )
   two_half = _project(
      [
         _skater( 1, 20.0 ),
         _skater( 2, 20.0, 0.5 ),
         _skater( 3, 20.0 ),
         _skater( 4, 20.0, 0.5 ),
         *_six()[ 4: ],
      ],
      [] )
   assert _toi( two_half, 1 ) > _toi( one_half, 1 )


def Test_Project_TestHalfAvailable_ExpectMoreThanHealthyShare() -> None:
   even = _project( _six(), [ _skater( 7, 16.0 ) ] )
   mixed = _project( _six( 0.5 ), [ _skater( 7, 16.0 ) ] )
   assert _toi( mixed, 1 ) > _toi( even, 1 )


def Test_Project_TestForwardPie_ExpectOneEighty() -> None:
   regulars = [
      _skater( index, 15.0 )
      for index in range( 1, NhlLineupSelector.DRESSED_FORWARDS + 1 )
   ]
   projected = IceAllocator.project(
      regulars,
      [],
      [],
      DepthGroup.forwards() )
   total = sum( toi for _skater_row, toi in projected )
   assert abs( total - DepthGroup.FORWARD_ICE_MINUTES ) < 0.001
