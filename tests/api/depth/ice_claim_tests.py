from __future__ import annotations

from api.depth.club_ice import ClubIce
from api.depth.ice_claim import IceClaim
from api.shared.enums.position import Position
from api.skaters.team import Team


def Test_Resolve_TestMissingRate_ExpectLastToi() -> None:
   team = list( Team )[ Position.FIRST ]
   toi = 22.0

   claim = IceClaim.resolve( [ ClubIce( team, 82, toi ) ], {} )

   assert claim == toi


def Test_Resolve_TestTeamRate_ExpectScaledToi() -> None:
   team = list( Team )[ Position.FIRST ]
   toi = 22.0
   rate = 0.8

   claim = IceClaim.resolve( [ ClubIce( team, 82, toi ) ], { team: rate } )

   assert claim == toi * rate


def Test_Resolve_TestSplitClubs_ExpectGamesWeightedClaim() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
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
   rates = { first: first_rate, second: second_rate }

   claim = IceClaim.resolve( clubs, rates )

   assert claim == (
      first_toi * first_rate * first_games
      + second_toi * second_rate * second_games
   ) / ( first_games + second_games )
