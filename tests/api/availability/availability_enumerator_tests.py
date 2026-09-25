from __future__ import annotations

from api.availability.availability_enumerator import AvailabilityEnumerator
from api.depth.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _skater( player_id: int, availability: float ) -> IceSkater:
   return IceSkater(
      player_id,
      str( player_id ),
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      20.0,
      20.0,
      availability )


def Test_Resolve_TestOneHalfAvailable_ExpectInAndOut() -> None:
   availability = 0.5
   skater = _skater( 1, availability )
   skaters = [ skater ]

   states = AvailabilityEnumerator.resolve( skaters )

   in_state = next( state for state in states if not state.regulars_out )
   out_state = next( state for state in states if state.regulars_out )
   assert len( states ) == 2
   assert abs( in_state.share - availability ) < 0.001
   assert abs( out_state.share - ( 1.0 - availability ) ) < 0.001
   assert in_state.playing == skaters
   assert out_state.playing == []


def Test_GamesOut_TestTwoHalfAvailable_ExpectQuarterTwoOut() -> None:
   availability = 0.5
   pace_games = 4
   skaters = [ _skater( 1, availability ), _skater( 2, availability ) ]

   mix = AvailabilityEnumerator.games_out( skaters, pace_games )

   assert abs( mix[ Position.FIRST ] - 0.25 * pace_games ) < 0.001
   assert abs( mix[ Position.SECOND ] - 0.5 * pace_games ) < 0.001
   assert abs( mix[ Position.THIRD ] - 0.25 * pace_games ) < 0.001
   assert abs( sum( mix ) - pace_games ) < 0.001
