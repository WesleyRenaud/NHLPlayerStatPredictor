from __future__ import annotations

from api.depth.ice_skater_assembler import IceSkaterAssembler
from api.depth.ice_usage import IceUsage
from api.shared.enums.position import Position
from api.skaters.roster_skater import RosterSkater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def Test_Build_TestUsage_ExpectLastToi() -> None:
   now = Team( 'CHI' )
   last = Team( 'BUF' )
   roster = [
      RosterSkater( 1, 'Bowen Byram', SkaterPosition( 'D' ), now ),
      RosterSkater( 2, 'Kid', SkaterPosition( 'D' ), now ),
   ]
   ice_usages = {
      1: IceUsage( 22.34, 82, last, SkaterPosition( 'D' ) ),
   }
   skaters = IceSkaterAssembler.build(
      roster,
      ice_usages,
      { 1: 1.0, 2: 1.0 } )
   assert skaters[ Position.FIRST ].implied == 22.34
   assert skaters[ Position.FIRST ].last_toi == 22.34
   assert skaters[ Position.SECOND ].implied == 0.0
   assert skaters[ Position.SECOND ].last_toi is None


def Test_Build_TestAvailability_ExpectProjectedShare() -> None:
   team = list( Team )[ Position.FIRST ]
   skaters = IceSkaterAssembler.build(
      [ RosterSkater( 1, 'A', SkaterPosition( 'D' ), team ) ],
      {},
      { 1: 0.62 } )
   assert skaters[ Position.FIRST ].availability == 0.62
