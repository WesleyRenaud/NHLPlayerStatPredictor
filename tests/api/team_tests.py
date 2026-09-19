from __future__ import annotations

import pytest

from api.team import Team


@pytest.mark.parametrize( 'team, code', [
   ( Team.ANAHEIM_DUCKS, 'ANA' ),
   ( Team.ARIZONA_COYOTES, 'ARI' ),
   ( Team.ATLANTA_THRASHERS, 'ATL' ),
   ( Team.BOSTON_BRUINS, 'BOS' ),
   ( Team.BUFFALO_SABRES, 'BUF' ),
   ( Team.CALGARY_FLAMES, 'CGY' ),
   ( Team.CAROLINA_HURRICANES, 'CAR' ),
   ( Team.CHICAGO_BLACKHAWKS, 'CHI' ),
   ( Team.COLORADO_AVALANCHE, 'COL' ),
   ( Team.COLUMBUS_BLUE_JACKETS, 'CBJ' ),
   ( Team.DALLAS_STARS, 'DAL' ),
   ( Team.DETROIT_RED_WINGS, 'DET' ),
   ( Team.EDMONTON_OILERS, 'EDM' ),
   ( Team.FLORIDA_PANTHERS, 'FLA' ),
   ( Team.LOS_ANGELES_KINGS, 'LAK' ),
   ( Team.MINNESOTA_WILD, 'MIN' ),
   ( Team.MONTREAL_CANADIENS, 'MTL' ),
   ( Team.NASHVILLE_PREDATORS, 'NSH' ),
   ( Team.NEW_JERSEY_DEVILS, 'NJD' ),
   ( Team.NEW_YORK_ISLANDERS, 'NYI' ),
   ( Team.NEW_YORK_RANGERS, 'NYR' ),
   ( Team.OTTAWA_SENATORS, 'OTT' ),
   ( Team.PHILADELPHIA_FLYERS, 'PHI' ),
   ( Team.PHOENIX_COYOTES, 'PHX' ),
   ( Team.PITTSBURGH_PENGUINS, 'PIT' ),
   ( Team.SAN_JOSE_SHARKS, 'SJS' ),
   ( Team.SEATTLE_KRAKEN, 'SEA' ),
   ( Team.ST_LOUIS_BLUES, 'STL' ),
   ( Team.TAMPA_BAY_LIGHTNING, 'TBL' ),
   ( Team.TORONTO_MAPLE_LEAFS, 'TOR' ),
   ( Team.UTAH_MAMMOTH, 'UTA' ),
   ( Team.VANCOUVER_CANUCKS, 'VAN' ),
   ( Team.VEGAS_GOLDEN_KNIGHTS, 'VGK' ),
   ( Team.WASHINGTON_CAPITALS, 'WSH' ),
   ( Team.WINNIPEG_JETS, 'WPG' ),
] )
def Test_Code( team: Team, code: str ) -> None:
   assert team == code
