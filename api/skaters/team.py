from __future__ import annotations

from enum import Enum
import unicodedata

from .team_name_change import TeamNameChange


class Team( str, Enum ):
   ANAHEIM_DUCKS = 'ANA'
   ARIZONA_COYOTES = 'ARI'
   ATLANTA_THRASHERS = 'ATL'
   BOSTON_BRUINS = 'BOS'
   BUFFALO_SABRES = 'BUF'
   CALGARY_FLAMES = 'CGY'
   CAROLINA_HURRICANES = 'CAR'
   CHICAGO_BLACKHAWKS = 'CHI'
   COLORADO_AVALANCHE = 'COL'
   COLUMBUS_BLUE_JACKETS = 'CBJ'
   DALLAS_STARS = 'DAL'
   DETROIT_RED_WINGS = 'DET'
   EDMONTON_OILERS = 'EDM'
   FLORIDA_PANTHERS = 'FLA'
   LOS_ANGELES_KINGS = 'LAK'
   MINNESOTA_WILD = 'MIN'
   MONTREAL_CANADIENS = 'MTL'
   NASHVILLE_PREDATORS = 'NSH'
   NEW_JERSEY_DEVILS = 'NJD'
   NEW_YORK_ISLANDERS = 'NYI'
   NEW_YORK_RANGERS = 'NYR'
   OTTAWA_SENATORS = 'OTT'
   PHILADELPHIA_FLYERS = 'PHI'
   PHOENIX_COYOTES = 'PHX'
   PITTSBURGH_PENGUINS = 'PIT'
   SAN_JOSE_SHARKS = 'SJS'
   SEATTLE_KRAKEN = 'SEA'
   ST_LOUIS_BLUES = 'STL'
   TAMPA_BAY_LIGHTNING = 'TBL'
   TORONTO_MAPLE_LEAFS = 'TOR'
   UTAH_MAMMOTH = 'UTA'
   VANCOUVER_CANUCKS = 'VAN'
   VEGAS_GOLDEN_KNIGHTS = 'VGK'
   WASHINGTON_CAPITALS = 'WSH'
   WINNIPEG_JETS = 'WPG'


   @classmethod
   def from_name( cls, name: str ) -> Team:
      ascii_name = unicodedata.normalize( 'NFKD', name ).encode(
         'ascii',
         'ignore' ).decode()
      key = ascii_name.upper().replace( '.', '' ).replace( "'", '' ).strip()
      key = key.replace( ' ', '_' )
      return cls[ TeamNameChange.current( key ) ]
