from __future__ import annotations

from .nhl_client import NhlClient
from .roster_skater import RosterSkater
from .roster_skater_builder import RosterSkaterBuilder
from .team import Team
from .types import Types


class RosterSkaterIngester():
   @classmethod
   def build_rows( cls, force: bool = False ) -> list[ RosterSkater ]:
      rows: list[ RosterSkater ] = []
      seen: set[ int ] = set()

      for team in cls._teams( NhlClient.standings( force=force ) ):
         print( f'Fetching roster { team.value }...', flush=True )

         for row in RosterSkaterBuilder.build(
               team,
               NhlClient.roster( team.value, force=force ) ):
            if row.player_id in seen:
               continue

            seen.add( row.player_id )
            rows.append( row )

      return rows


   @classmethod
   def _teams( cls, standings: Types.JsonObject ) -> list[ Team ]:
      raw_rows = standings[ 'standings' ]

      if not isinstance( raw_rows, list ):
         raise TypeError( 'standings' )

      teams: list[ Team ] = []
      seen: set[ Team ] = set()

      for raw in raw_rows:
         if not isinstance( raw, dict ):
            continue

         team = Team( cls._abbrev( raw ) )

         if team in seen:
            continue

         seen.add( team )
         teams.append( team )

      return sorted( teams, key=lambda team: team.value )


   @classmethod
   def _abbrev( cls, raw: Types.JsonObject ) -> str:
      abbrev = raw[ 'teamAbbrev' ]

      if not isinstance( abbrev, dict ):
         raise TypeError( 'teamAbbrev' )

      return str( abbrev[ 'default' ] )
