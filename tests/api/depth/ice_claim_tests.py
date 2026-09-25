from __future__ import annotations

from api.depth.ice_claim import IceClaim
from api.shared.enums.position import Position
from api.skaters.team import Team


def Test_Resolve_TestMissingRate_ExpectLastToi() -> None:
   team = list( Team )[ Position.FIRST ]
   assert IceClaim.resolve( 22.0, team, {} ) == 22.0


def Test_Resolve_TestTeamRate_ExpectScaledToi() -> None:
   team = list( Team )[ Position.FIRST ]
   assert IceClaim.resolve( 22.0, team, { team: 0.8 } ) == 17.6
