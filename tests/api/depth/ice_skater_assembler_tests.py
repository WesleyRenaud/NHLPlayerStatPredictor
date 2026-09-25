from __future__ import annotations

from api.depth.club_ice import ClubIce
from api.depth.ice_claim import IceClaim
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
      { 1: 1.0, 2: 1.0 },
      {},
      {} )
   assert skaters[ Position.FIRST ].implied == 22.34
   assert skaters[ Position.FIRST ].last_toi == 22.34
   assert skaters[ Position.SECOND ].implied == 0.0
   assert skaters[ Position.SECOND ].last_toi is None


def Test_Build_TestTeamRate_ExpectScaledClaim() -> None:
   now = Team( 'CHI' )
   last = Team( 'BUF' )
   roster = [
      RosterSkater( 1, 'Bowen Byram', SkaterPosition( 'D' ), now ),
   ]
   ice_usages = {
      1: IceUsage( 22.0, 82, last, SkaterPosition( 'D' ) ),
   }
   skaters = IceSkaterAssembler.build(
      roster,
      ice_usages,
      { 1: 1.0 },
      { last: 0.8 },
      {} )
   assert skaters[ Position.FIRST ].implied == 17.6
   assert skaters[ Position.FIRST ].last_toi == 22.0


def Test_Build_TestAvailability_ExpectProjectedShare() -> None:
   team = list( Team )[ Position.FIRST ]
   skaters = IceSkaterAssembler.build(
      [ RosterSkater( 1, 'A', SkaterPosition( 'D' ), team ) ],
      {},
      { 1: 0.62 },
      {},
      {} )
   assert skaters[ Position.FIRST ].availability == 0.62


def Test_Build_TestSplitClubs_ExpectMixedClaim() -> None:
   now = list( Team )[ Position.FIRST ]
   first = list( Team )[ Position.SECOND ]
   second = list( Team )[ Position.THIRD ]
   first_games = 50
   second_games = 22
   first_toi = 14.0
   second_toi = 12.0
   first_rate = 0.8
   second_rate = 1.2
   last_toi = 13.67
   skaters = IceSkaterAssembler.build(
      [ RosterSkater( 1, 'A', SkaterPosition( 'C' ), now ) ],
      { 1: IceUsage( last_toi, 72, second, SkaterPosition( 'C' ) ) },
      { 1: 1.0 },
      { first: first_rate, second: second_rate },
      {
         1: [
            ClubIce( first, first_games, first_toi ),
            ClubIce( second, second_games, second_toi ),
         ]
      } )
   assert skaters[ Position.FIRST ].implied == IceClaim.resolve(
      [
         ClubIce( first, first_games, first_toi ),
         ClubIce( second, second_games, second_toi ),
      ],
      { first: first_rate, second: second_rate } )
   assert skaters[ Position.FIRST ].last_toi == last_toi
