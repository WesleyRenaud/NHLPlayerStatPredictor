from __future__ import annotations

from api.depth.club_ice import ClubIce
from api.depth.ice_claim import IceClaim
from api.shared.enums.position import Position
from api.skaters.team import Team


def Test_Resolve_TestSingleClub_ExpectLastToi() -> None:
   team = list( Team )[ Position.FIRST ]
   toi = 22.0

   claim = IceClaim.resolve( [ ClubIce( team, 82, toi ) ] )

   assert claim == toi


def Test_Resolve_TestDifferentClub_ExpectUnscaledToi() -> None:
   team = list( Team )[ Position.FIRST ]
   toi = 22.0

   claim = IceClaim.resolve( [ ClubIce( team, 82, toi ) ] )

   assert claim == toi


def Test_Resolve_TestSplitClubs_ExpectGamesWeightedClaim() -> None:
   first = list( Team )[ Position.FIRST ]
   second = list( Team )[ Position.SECOND ]
   first_games = 50
   second_games = 22
   first_toi = 14.0
   second_toi = 12.0
   clubs = [
      ClubIce( first, first_games, first_toi ),
      ClubIce( second, second_games, second_toi ),
   ]

   claim = IceClaim.resolve( clubs )

   assert claim == (
      first_toi * first_games
      + second_toi * second_games
   ) / ( first_games + second_games )
