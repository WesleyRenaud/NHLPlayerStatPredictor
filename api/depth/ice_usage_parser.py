from __future__ import annotations

from .ice_usage import IceUsage
from ..season import Season
from ..skaters.skater_position import SkaterPosition
from ..skaters.team import Team
from ..time import Time
from ..types import Types


class IceUsageParser():
   @classmethod
   def parse( cls, rows: Types.JsonObjectList ) -> dict[ int, IceUsage ]:
      usages: dict[ int, IceUsage ] = {}

      for row in rows:
         usages[ int( row[ 'playerId' ] ) ] = IceUsage(
            Time.minutes( float( row[ 'timeOnIcePerGame' ] ) ),
            int( row[ 'gamesPlayed' ] ),
            Season.primary_team( [
               Team( part )
               for part in str( row[ 'teamAbbrevs' ] ).split( ',' )
            ] ),
            SkaterPosition( str( row[ 'positionCode' ] ) ) )

      return usages
