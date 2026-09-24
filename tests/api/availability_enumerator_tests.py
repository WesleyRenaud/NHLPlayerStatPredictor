from __future__ import annotations

from api.availability_enumerator import AvailabilityEnumerator
from api.ice_skater import IceSkater
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.team import Team


def _skater( player_id: int, availability: float ) -> IceSkater:
   return IceSkater(
      player_id,
      str( player_id ),
      SkaterPosition( 'D' ),
      list( Team )[ Position.FIRST ],
      20.0,
      20.0,
      80,
      False,
      availability )


def Test_Resolve_TestOneHalfAvailable_ExpectInAndOut() -> None:
   states = AvailabilityEnumerator.resolve( [ _skater( 1, 0.5 ) ] )
   in_state = next( state for state in states if not state.regulars_out )
   out_state = next( state for state in states if state.regulars_out )
   assert len( states ) == 2
   assert abs( in_state.share - 0.5 ) < 0.001
   assert abs( out_state.share - 0.5 ) < 0.001
   assert len( in_state.playing ) == 1
   assert out_state.playing == []


def Test_GamesOut_TestTwoHalfAvailable_ExpectQuarterTwoOut() -> None:
   pace_games = 4
   mix = AvailabilityEnumerator.games_out(
      [ _skater( 1, 0.5 ), _skater( 2, 0.5 ) ],
      pace_games )
   assert abs( mix[ Position.FIRST ] - 0.25 * pace_games ) < 0.001
   assert abs( mix[ Position.SECOND ] - 0.5 * pace_games ) < 0.001
   assert abs( mix[ Position.THIRD ] - 0.25 * pace_games ) < 0.001
   assert abs( sum( mix ) - pace_games ) < 0.001
