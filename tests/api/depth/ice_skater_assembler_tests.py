from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.club_ice import ClubIce
from api.depth.ice_claim import IceClaim
from api.depth.ice_skater_assembler import IceSkaterAssembler
from api.depth.usable_nhl_ice import UsableNhlIce
from api.shared.enums.position import Position
from api.skaters.roster_skater import RosterSkater
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _ice( toi: float, team: Team, games: int = 82 ) -> UsableNhlIce:
   return UsableNhlIce( 20252026, toi, [ ClubIce( team, games, toi ) ] )


def Test_Build_TestUsage_ExpectLastToi() -> None:
   now = list( Team )[ Position.FIRST ]
   last = list( Team )[ Position.SECOND ]
   toi = 22.34
   roster = [
      RosterSkater( 1, 'Bowen Byram', SkaterPosition( 'D' ), now ),
      RosterSkater( 2, 'Kid', SkaterPosition( 'D' ), now ),
   ]

   skaters = IceSkaterAssembler.build(
      roster,
      { 1: _ice( toi, last ) },
      { 1: GamesShare.FULL, 2: GamesShare.FULL },
      {} )

   assert skaters[ Position.FIRST ].implied == toi
   assert skaters[ Position.FIRST ].last_toi == toi
   assert skaters[ Position.SECOND ].implied == 0.0
   assert skaters[ Position.SECOND ].last_toi is None


def Test_Build_TestTeamRate_ExpectScaledClaim() -> None:
   now = list( Team )[ Position.FIRST ]
   last = list( Team )[ Position.SECOND ]
   toi = 22.0
   rate = 0.8

   skaters = IceSkaterAssembler.build(
      [ RosterSkater( 1, 'Bowen Byram', SkaterPosition( 'D' ), now ) ],
      { 1: _ice( toi, last ) },
      { 1: GamesShare.FULL },
      { last: rate } )

   assert skaters[ Position.FIRST ].implied == toi * rate
   assert skaters[ Position.FIRST ].last_toi == toi


def Test_Build_TestAvailability_ExpectProjectedShare() -> None:
   team = list( Team )[ Position.FIRST ]
   availability = 0.62

   skaters = IceSkaterAssembler.build(
      [ RosterSkater( 1, 'A', SkaterPosition( 'D' ), team ) ],
      {},
      { 1: availability },
      {} )

   assert skaters[ Position.FIRST ].availability == availability


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
   clubs = [
      ClubIce( first, first_games, first_toi ),
      ClubIce( second, second_games, second_toi ),
   ]
   last_toi = (
      first_toi * first_games + second_toi * second_games
   ) / ( first_games + second_games )
   rates = { first: first_rate, second: second_rate }

   skaters = IceSkaterAssembler.build(
      [ RosterSkater( 1, 'A', SkaterPosition( 'C' ), now ) ],
      { 1: UsableNhlIce( 20252026, last_toi, clubs ) },
      { 1: GamesShare.FULL },
      rates )

   assert skaters[ Position.FIRST ].implied == IceClaim.resolve( clubs, rates )
   assert skaters[ Position.FIRST ].last_toi == last_toi
